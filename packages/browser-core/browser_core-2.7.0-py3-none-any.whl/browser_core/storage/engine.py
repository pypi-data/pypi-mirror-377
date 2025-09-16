# Define o motor de armazenamento de baixo nível para a gestão de snapshots.
#
# Este módulo implementa o StorageEngine, que utiliza uma abordagem de
# armazenamento endereçável por conteúdo (semelhante ao Git) para gerenciar
# os arquivos de perfis de navegador de forma extremamente eficiente.

import fnmatch
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from ..exceptions import StorageEngineError
from ..types import FilePath, ObjectHash, RelativePath
from ..utils import ensure_directory


class StorageEngine:
    """
    Motor de armazenamento baseado em conteúdo (content-addressable storage).

    É responsável por três operações críticas:
    1. Calcular a diferença (delta) entre dois estados de diretório.
    2. Armazenar cada arquivo (objeto) de forma única, usando seu hash de
       conteúdo como identificador, eliminando a redundância.
    3. Materializar um diretório de trabalho funcional, compondo uma
       sequência de deltas para reconstruir um estado específico.
    """

    def __init__(self, objects_dir: FilePath):
        """
        Inicializa o motor de armazenamento.

        Args:
            objects_dir: O diretório raiz onde os objetos (arquivos com hash)
                         serão armazenados. Ex: ".../browser-core-output/objects".
        """
        self.objects_dir = ensure_directory(objects_dir)

    @staticmethod
    def _hash_file(file_path: Path) -> ObjectHash:
        """
        Calcula o hash SHA256 do conteúdo de um arquivo.

        Args:
            file_path: O caminho para o arquivo a ser processado.

        Returns:
            O hash SHA256 em formato hexadecimal.
        """
        h = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except IOError as e:
            raise StorageEngineError(
                f"Não foi possível ler o arquivo para calcular o hash: {file_path}",
                original_error=e,
            )

    def store_object_from_path(self, source_path: Path) -> ObjectHash:
        """
        Armazena um arquivo do sistema de arquivos no diretório de objetos.

        Se um objeto com o mesmo conteúdo já existe, ele não é armazenado
        novamente, economizando espaço. O método é idempotente.

        Args:
            source_path: O caminho do arquivo de origem a ser armazenado.

        Returns:
            O hash SHA256 do conteúdo do arquivo, que serve como seu ID no
            armazenamento de objetos.
        """
        file_hash = self._hash_file(source_path)
        object_path = self.objects_dir / file_hash

        if not object_path.exists():
            try:
                shutil.copy(source_path, object_path)
            except IOError as e:
                raise StorageEngineError(
                    f"Falha ao copiar o arquivo para o armazenamento de objetos: {source_path}",
                    original_error=e,
                )

        return file_hash

    def calculate_delta(
        self, base_dir: Path, new_dir: Path
    ) -> Dict[RelativePath, ObjectHash]:
        """
        Calcula a diferença (delta) entre um diretório base e um novo estado.

        Compara o 'new_dir' com o 'base_dir' e retorna um dicionário
        mapeando os caminhos relativos para os hashes de conteúdo dos arquivos
        que foram adicionados ou modificados.

        Args:
            base_dir: O diretório que representa o estado "antigo" ou "pai".
            new_dir: O diretório que representa o estado "novo" ou "filho".

        Returns:
            Um dicionário representando o "diff" entre os diretórios.
        """
        delta: Dict[RelativePath, ObjectHash] = {}

        ignore_patterns: List[str] = []
        ignore_file = new_dir / ".snapshotignore"
        if ignore_file.exists():
            try:
                with open(ignore_file, "r", encoding="utf-8") as f:
                    ignore_patterns = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.strip().startswith("#")
                    ]
            except IOError:
                pass

        def should_ignore(rel_path: str) -> bool:
            return any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_patterns)

        base_files: Dict[RelativePath, Tuple[int, ObjectHash]] = {}
        for p in base_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(base_dir))
                if should_ignore(rel):
                    continue
                base_files[rel] = (
                    p.stat().st_size,
                    self._hash_file(p),
                )

        for new_file in new_dir.rglob("*"):
            if not new_file.is_file():
                continue

            relative_path = str(new_file.relative_to(new_dir))
            if should_ignore(relative_path):
                continue
            new_size = new_file.stat().st_size

            # Compara metadados (tamanho) antes de calcular o hash.
            base_file_meta = base_files.get(relative_path)
            if base_file_meta and base_file_meta[0] == new_size:
                # O tamanho é o mesmo, agora verifica o hash como confirmação final.
                new_hash = self._hash_file(new_file)
                if base_file_meta[1] == new_hash:
                    continue  # O arquivo é idêntico, pular.
            else:
                # O arquivo é novo ou o tamanho mudou, então o hash precisa ser calculado.
                new_hash = self._hash_file(new_file)

            # Se chegamos aqui, o arquivo é novo ou modificado.
            self.store_object_from_path(new_file)
            delta[relative_path] = new_hash

        return delta

    def materialize(
        self, deltas: List[Dict[RelativePath, ObjectHash]], target_dir: Path
    ) -> None:
        """
        Materializa um estado final aplicando uma sequência de deltas sobre um diretório.

        Constrói (ou reconstrói) um diretório de trabalho 'target_dir' ao
        mesclar os deltas em ordem. Deltas mais recentes sobrescrevem os
        arquivos das camadas anteriores.

        Args:
            deltas: Uma lista de dicionários de delta, do mais antigo (base)
                    para o mais novo.
            target_dir: O diretório de destino onde o perfil será construído.
                        O conteúdo existente será removido.
        """
        if target_dir.exists():
            shutil.rmtree(target_dir)
        ensure_directory(target_dir)

        # Mescla todos os deltas em um único dicionário de estado final.
        # A ordem garante que deltas posteriores (mais novos) sobrescrevam os anteriores.
        final_state: Dict[RelativePath, ObjectHash] = {}
        for delta in deltas:
            final_state.update(delta)

        # Constrói o diretório de trabalho a partir do estado final.
        for rel_path, obj_hash in final_state.items():
            object_path = self.objects_dir / obj_hash
            destination_path = target_dir / rel_path

            if not object_path.exists():
                raise StorageEngineError(
                    f"Objeto '{obj_hash}' referenciado por '{rel_path}' não foi "
                    "encontrado no armazenamento. O repositório pode estar corrompido."
                )

            # Garante que a estrutura de subdiretórios exista.
            ensure_directory(destination_path.parent)
            try:
                # Copia o objeto do armazenamento para o diretório de trabalho.
                shutil.copy(object_path, destination_path)
            except IOError as e:
                raise StorageEngineError(
                    f"Falha ao materializar o objeto '{obj_hash}' em '{destination_path}'",
                    original_error=e,
                )
