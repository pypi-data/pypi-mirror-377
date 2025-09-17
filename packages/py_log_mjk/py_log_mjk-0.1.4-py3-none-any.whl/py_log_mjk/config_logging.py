import atexit
import json
import logging
import importlib.resources
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener

from py_log_mjk.settings import LogLevel, settings

_setup_logging_done: bool = False
_default_queue_listener: QueueListener | None = None

_logger = logging.getLogger(settings.setup_logger_name)
_logger.setLevel(settings.setup_logger_level)


def _get_logging_config() -> dict:
    """Carrega a configuração de logging.
    
    1. Primeiro tenta o caminho absoluto definido pelo usuário.
    2. Se não existir, usa o JSON do pacote `templates/` como fallback.
    """
    # Caminho absoluto fornecido pelo usuário
    if settings.logging_config_json_path.is_file():
        with settings.logging_config_json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback: JSON interno da lib (templates)
    try:
        package = importlib.resources.files("py_log_mjk.templates")
        config_file_path = package / "default_logging.conf.json"
        with importlib.resources.as_file(config_file_path) as path:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        msg = f"Não foi possível carregar a configuração de logging: {e}"
        _logger.error(msg)
        raise FileNotFoundError(msg)

def _setup_queue_listener() -> None:
    """Inicia o QueueListener e registra a função de parada."""
    global _default_queue_listener
    
    queue_handlers = [
        handler for handler in logging.getLogger().handlers if isinstance(handler, QueueHandler)
    ]
    
    if len(queue_handlers) > 1:
        msg = "This function does not allow more than one QueueHandler"
        raise RuntimeError(msg)
        
    if not queue_handlers:
        return

    queue_handler = queue_handlers[0]
    _logger.debug("Found QueueHandler with name: '%s'", queue_handler.name)
    _default_queue_listener = queue_handler.listener
    
    if _default_queue_listener:
        _default_queue_listener.start()
        atexit.register(_stop_queue_listener)
        _logger.debug("QueueListener started and registered with atexit.")


def _stop_queue_listener() -> None:
    """Para o QueueListener de forma controlada."""
    if _default_queue_listener:
        _logger.debug("Stopping listener...")
        _default_queue_listener.stop()


def _configure_logging() -> None:
    """Configura o sistema de logging do Python."""
    global _setup_logging_done
    
    if _setup_logging_done:
        _logger.debug("Logging already configured.")
        return

    settings.validate_paths()

    try:
        config = _get_logging_config()
        dictConfig(config)
        _logger.debug("JSON config file loaded and applied.")
        _setup_queue_listener()
        _setup_logging_done = True
    except Exception as e:
        _logger.exception("Failed to configure logging. Using basic config.")
        logging.basicConfig(level=settings.default_logger_level)
        _setup_logging_done = True


def get_logger(name: str = __name__, level: LogLevel | None = None) -> logging.Logger:
    """
    Obtém um logger configurado. Se o logging ainda não foi configurado,
    configura-o automaticamente.
    """
    _configure_logging()
    
    logger = logging.getLogger(name)
    
    if level is not None:
        logger.setLevel(settings._validate_level(level))
        _logger.debug(f"Level '{level}' set for logger '{name}'.")
    else:
        logger.setLevel(settings.default_logger_level)
        _logger.debug(f"Default level '{settings.default_logger_level}' set for logger '{name}'.")
        
    return logger