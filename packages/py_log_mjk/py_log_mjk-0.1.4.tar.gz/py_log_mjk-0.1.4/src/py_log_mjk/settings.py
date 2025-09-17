from os import getenv
from pathlib import Path
from typing import Literal

# Tipos de nível de log válidos
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ALLOWED_LEVELS: set[LogLevel] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings:
    """Encapsula e valida as configurações da biblioteca."""

    def __init__(self) -> None:
        self.root_dir: Path = Path(".").resolve()

        # Diretório de logs
        self.logs_dir: Path = self.root_dir / getenv("LOGS_DIR", "logs")

        # Arquivo de configuração JSON
        self.logging_config_json_path: Path = Path(getenv("LOGGING_CONFIG_JSON", "default_logging.conf.json"))

        # Nome e nível do logger de setup
        self.setup_logger_name: str = getenv("SETUP_LOGGER_NAME", "py_log_mjk.config_setup")
        self.setup_logger_level: LogLevel = self._validate_level(
            getenv("SETUP_LOGGER_LEVEL", "DEBUG")
        )

        # Nível padrão do logger
        self.default_logger_level: LogLevel = self._validate_level(
            getenv("DEFAULT_LOGGER_LEVEL", "DEBUG")
        )

        # Garante que o diretório de logs exista
        self.validate_paths()

    @staticmethod
    def _validate_level(level: str) -> LogLevel:
        if level not in ALLOWED_LEVELS:
            msg = f"Level {level!r} is not allowed. Use one of these: {ALLOWED_LEVELS}"
            raise ValueError(msg)
        return level

    def validate_paths(self) -> None:
        """Valida se os caminhos de diretórios e arquivos existem."""
        if not self.logs_dir.is_dir():
            self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Se o arquivo JSON não existir, a lib pode usar o default interno
        if not self.logging_config_json_path.is_file():
            # Você pode colocar aqui um fallback ou apenas logar a ausência
            pass


# Instância global das configurações
settings = Settings()
