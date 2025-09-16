"""
Define todos os tipos de dados, Enums e Protocolos para o 'browser-core'.

Este arquivo centraliza as estruturas de dados, garantindo consistência
e permitindo a verificação estática de tipos no framework. É um
componente chave para um código robusto e de fácil manutenção.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union, Callable

from typing_extensions import TypedDict

# ==============================================================================
# --- Tipos Primitivos e Aliases ---
# ==============================================================================

TimeoutMs = int
"""Representa um valor de tempo em milissegundos."""

FilePath = Union[str, Path]
"""Representa um caminho de arquivo, que pode ser uma string ou um objeto Path."""

SelectorValue = str
"""Representa o valor de um seletor de elemento da web (ex: '//div[@id="main"]')."""

ElementIndex = int
"""Representa o índice de um elemento em uma lista de elementos."""

# --- Novos Tipos para a Arquitetura ---
SnapshotId = str
"""Representa o identificador único de um snapshot (ex: 'chrome_115_logged_in')."""

ObjectHash = str
"""Representa o hash SHA256 do conteúdo de um arquivo."""

RelativePath = str
"""Representa o caminho relativo de um arquivo dentro de um perfil de navegador."""

# Tipo explícito para o Delta ---
SnapshotDelta = Dict[RelativePath, ObjectHash]
"""
Define um 'delta', mapeando caminhos relativos de arquivos para seus hashes.
Representa as mudanças entre um snapshot e seu pai.
Ex: {"Default/Cookies": "hash123", "Extensions/uBlock/manifest.json": "hash456"}
"""


# ==============================================================================
# --- Enums para Valores Controlados ---
# ==============================================================================


class BrowserType(Enum):
    """Define os tipos de navegadores suportados pela automação."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class SelectorType(Enum):
    """Define os tipos de seletores de elementos da web suportados."""

    XPATH = "xpath"
    CSS = "css"
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class_name"
    TAG_NAME = "tag_name"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"


class LogLevel(Enum):
    """Define os níveis de log padrão."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TaskStatus(Enum):
    """Define os possíveis status de uma tarefa processada pelo WorkforceManager."""

    SUCCESS = "SUCCESS"
    SETUP_FAILED = "SETUP_FAILED"
    TASK_FAILED = "TASK_FAILED"


# ==============================================================================
# --- Dicionários de Configuração (TypedDicts) ---
# ==============================================================================


class BrowserConfig(TypedDict, total=False):
    """
    Define a estrutura para as configurações do navegador que um Worker pode usar.
    """

    headless: bool
    window_width: int
    window_height: int
    user_agent: Optional[str]
    incognito: bool
    disable_gpu: bool
    additional_args: List[str]
    # Anti-bot/stealth helpers
    proxy: Optional[str]
    random_user_agent: bool
    stealth: bool


class TimeoutConfig(TypedDict, total=False):
    """Define a estrutura para as configurações de timeout (em ms)."""

    element_find_ms: TimeoutMs
    page_load_ms: TimeoutMs
    script_ms: TimeoutMs
    # Adicionado em uma etapa anterior para consistência
    window_management_ms: TimeoutMs


class ThrottleConfig(TypedDict, total=False):
    """Define atrasos opcionais para humanizar ações (em ms)."""

    min_action_delay_ms: TimeoutMs
    max_action_delay_ms: TimeoutMs


class LoggingConfig(TypedDict, total=False):
    """Define a estrutura para as configurações de logging."""

    level: str
    to_file: bool
    to_console: bool
    format_type: str
    mask_credentials: bool


class PathsConfig(TypedDict, total=False):
    """
    Define a estrutura para os caminhos de saída personalizáveis.
    """

    output_dir: FilePath
    objects_dir: FilePath
    snapshots_metadata_dir: FilePath
    tasks_logs_dir: FilePath
    driver_cache_dir: FilePath


# ==============================================================================
# --- Estruturas de Dados da Arquitetura (TypedDicts) ---
# ==============================================================================


class DriverInfo(TypedDict):
    """Metadados sobre a versão do WebDriver vinculada a uma cadeia de snapshots."""

    name: str  # Ex: "chrome"
    version: str  # Ex: "115.0.5790.170"


class SnapshotData(TypedDict):
    """Define a estrutura completa de metadados para um snapshot, salva em JSON."""

    id: SnapshotId
    parent_id: Optional[SnapshotId]
    base_driver: DriverInfo
    created_at: str
    delta: SnapshotDelta
    metadata: Dict[str, Any]


class SquadConfig(TypedDict):
    """
    Define a configuração para um único esquadrão de workers a ser lançado
    pelo Orchestrator.
    """

    squad_name: str
    num_workers: int
    processing_function: Callable[..., Any]
    tasks_queue: str  # CORRIGIDO: O utilizador fornece o NOME da fila.


# ==============================================================================
# --- Protocolos para Inversão de Dependência (SOLID) ---
# ==============================================================================


class WebElementProtocol(Protocol):
    """Define o contrato mínimo para um WebElement, permitindo buscas aninhadas."""

    @property
    def text(self) -> str: ...

    @property
    def tag_name(self) -> str: ...

    def get_attribute(self, name: str) -> str: ...

    def click(self) -> None: ...

    def send_keys(self, *values: str) -> None: ...

    def clear(self) -> None: ...

    def is_displayed(self) -> bool: ...

    def is_enabled(self) -> bool: ...

    def is_selected(self) -> bool: ...

    def find_element(self, by: str, value: str) -> Any: ...

    def find_elements(self, by: str, value: str) -> List[Any]: ...


class SwitchToProtocol(Protocol):
    """Define o contrato para o objeto retornado por `driver.switch_to`."""

    def window(self, window_name: str) -> None: ...

    def frame(self, frame_reference: Any) -> None: ...

    def default_content(self) -> None: ...

    def parent_frame(self) -> None: ...

    @property
    def active_element(self) -> "WebElementProtocol": ...

    @property
    def alert(self) -> Any: ...


class WebDriverProtocol(Protocol):
    """Define o contrato mínimo que um objeto de WebDriver deve seguir."""

    @property
    def current_url(self) -> str: ...

    @property
    def title(self) -> str: ...

    @property
    def page_source(self) -> str: ...

    @property
    def current_window_handle(self) -> str: ...

    @property
    def window_handles(self) -> List[str]: ...

    def get(self, url: str) -> None: ...

    def quit(self) -> None: ...

    def close(self) -> None: ...

    def switch_to(self) -> "SwitchToProtocol": ...

    def find_element(self, by: str, value: str) -> WebElementProtocol: ...

    def find_elements(self, by: str, value: str) -> List[WebElementProtocol]: ...

    def execute_script(self, script: str, *args: Any) -> Any: ...

    def save_screenshot(self, filename: str) -> bool: ...

    def get_cookies(self) -> List[Dict[str, Any]]: ...

    def get_log(self, log_type: str) -> Any: ...

    def set_page_load_timeout(self, time_to_wait: float) -> None: ...

    def set_script_timeout(self, time_to_wait: float) -> None: ...


class LoggerProtocol(Protocol):
    """Define o contrato para um objeto de logger compatível."""

    def debug(self, msg: object, *args: object, **kwargs: Any) -> None: ...

    def info(self, msg: object, *args: object, **kwargs: Any) -> None: ...

    def warning(self, msg: object, *args: object, **kwargs: Any) -> None: ...

    def error(self, msg: object, *args: object, **kwargs: Any) -> None: ...

    def critical(self, msg: object, *args: object, **kwargs: Any) -> None: ...
