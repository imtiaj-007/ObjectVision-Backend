import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from app.configuration.config import settings


class LogConfig:
    """Centralized logging configuration"""

    LOG_LEVELS = {
        "TRACE": {"color": "\033[36m"},    # Cyan
        "DEBUG": {"color": "\033[34m"},     # Blue
        "INFO": {"color": "\033[34m"},      # Blue
        "SUCCESS": {"color": "\033[32m"},   # Green
        "WARNING": {"color": "\033[33m"},   # Yellow
        "ERROR": {"color": "\033[31m"},     # Red
        "CRITICAL": {"color": "\033[31;1m"} # Bold Red
    }
    RESET = "\033[0m"

    LOG_TYPES = {
        "app": {"level": "INFO", "filter": lambda r: r["level"].name == "INFO"},
        "error": {"level": "ERROR", "filter": lambda r: r["level"].name == "ERROR"},
        "db_error": {"level": "CRITICAL", "filter": lambda r: r.get("extra", {}).get("database") is not None},
        "audit": {"level": "INFO", "filter": lambda r: r.get("extra", {}).get("audit") is not None},
        "performance": {"level": "DEBUG", "filter": lambda r: r.get("extra", {}).get("performance") is not None}
    }

    def __init__(self):
        self.base_dir = Path(os.getcwd()) / "logs"
        self.log_dirs = {
            log_type: self.base_dir / f"{log_type}_logs"
            for log_type in self.LOG_TYPES
        }
        self._configure_logger()

    def _get_log_file_path(self, log_type: str) -> str:
        """Generate log file path with current date"""
        if log_type not in self.log_dirs:
            raise ValueError(f"Invalid log type: {log_type}")
        return str(self.log_dirs[log_type] / f"{log_type}_log_{datetime.now():%Y-%m-%d}.log")
    
    def flatten_dict(self, d):
        items = []
        for k, v in d.items():
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v).items())
            else:
                items.append((k, v))
        return dict(items)

    def _format_log_message(self, record: Dict[str, Any]) -> str:
        """Format log message with level-specific colors and icons"""
        level_name = record["level"].name
        level_config = self.LOG_LEVELS.get(level_name, {"color": "\033[37m"})
        color = level_config["color"]
        cur_time = record['time'].strftime("%Y-%m-%d %H:%M:%S")
        file = record['file'].name or None
        file_path = record['file'].path or None
        line_no = record['line'] or None
        
        msg = (
            f"{color}{level_name}{':':<5}{self.RESET}"
            f"[<cyan>{record['name']}</cyan>] "
            f"<green>{cur_time}</green> |=> \n"
            f"{f'[File]: {file:<10} | ' if file else ''}"
            f"{f'[File_Location]: {file_path:<10} | ' if file_path else ''}" \
            f"{f'[Line]: {line_no:<10}' if line_no else ''}"
            f"\n{color}{record['message']}{self.RESET}\n"
        )

        if record["extra"]:
            try:
                if isinstance(record["extra"], dict):
                    record["extra"] = self.flatten_dict(record["extra"])

                extras = []
                for k, v in record["extra"].items():
                    if v is None:
                        v = "None"
                    else:
                        v = str(v)
                    extras.append(f"{k}: {v}")
                if extras:
                    msg += f"<yellow>{' | '.join(extras)}</yellow>\n"
            except (KeyError, TypeError) as e:
                msg += f"<red>Error formatting extras: {str(e)}</red>\n"
        
        return f"{msg}\n"

    def _configure_logger(self) -> None:
        """Configure all logger instances"""
        logger.remove()

        # Create log directories
        for dir_path in self.log_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Common configuration
        common_config = {
            "format": self._format_log_message,
            "enqueue": True,
            "rotation": settings.LOG_ROTATION or "00:00",
            "retention": settings.LOG_RETENTION or "30 days",
            "compression": "zip",
            "serialize": True,
            "catch": True
        }

        # Configure log handlers
        for log_type, config in self.LOG_TYPES.items():
            logger.add(
                self._get_log_file_path(log_type),
                level=config["level"],
                filter=config["filter"],
                backtrace=config["level"] in ["ERROR", "CRITICAL"],
                diagnose=config["level"] in ["ERROR", "CRITICAL"],
                **common_config
            )

        # Add console handler for development
        if settings.ENVIORNMENT in ["development", "staging"]:
            logger.add(
                sys.stdout,
                format=self._format_log_message,
                level="DEBUG",
                colorize=True,
                backtrace=True,
                diagnose=True
            )

    def _log(self, level: str, message: str, **extra: Any) -> None:
        """Generic logging method"""
        if level not in self.LOG_LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        logger.bind(**extra).log(level, message)

    # Convenience methods using generic _log method
    def info(self, message: str, **extra: Any) -> None:
        self._log("INFO", message, **extra)

    def error(self, message: str, exc_info: bool = True, **extra: Any) -> None:
        self._log("ERROR", message, exc_info=exc_info, **extra)

    def success(self, message: str, **extra: Any) -> None:
        self._log("SUCCESS", message, **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self._log("WARNING", message, **extra)

    def debug(self, message: str, **extra: Any) -> None:
        self._log("DEBUG", message, **extra)

    def critical(self, message: str, exc_info: bool = True, **extra: Any) -> None:
        self._log("CRITICAL", message, exc_info=exc_info, **extra)

    def db_error(self, message: str, **extra: Any) -> None:
        self._log("CRITICAL", message, database=True, **extra)

    def audit(
        self,
        message: str,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        **extra: Any
    ) -> None:
        self._log("INFO", message, audit=True, user_id=user_id, action=action, **extra)

    def performance(
        self,
        message: str,
        duration: Optional[float] = None,
        endpoint: Optional[str] = None,
        **extra: Any
    ) -> None:
        self._log("DEBUG", message, performance=True, duration=duration, endpoint=endpoint, **extra)


# Initialize logger configuration
log = LogConfig()