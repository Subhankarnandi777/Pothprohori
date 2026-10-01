"""
Pothprohori – Structured JSON Logger
Uses loguru with a JSON sink for production and a pretty sink for development.
"""
import sys
import os
from loguru import logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENV = os.getenv("ENV", "development")


def _json_formatter(record: dict) -> str:
    import json
    from datetime import datetime

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }
    if record["exception"]:
        import traceback
        log_entry["exception"] = traceback.format_exc()
    if record.get("extra"):
        log_entry["extra"] = record["extra"]
    return json.dumps(log_entry, ensure_ascii=False) + "\n"


def configure_logging() -> None:
    """Configure loguru for the app. Call once at startup."""
    logger.remove()  # remove default handler

    if ENV == "production":
        # Production: JSON to stdout for log aggregators
        logger.add(
            sys.stdout,
            format=_json_formatter,
            level=LOG_LEVEL,
            serialize=False,
            enqueue=True,
        )
        # Rotating file log
        logger.add(
            "logs/pothprohori_{time:YYYY-MM-DD}.log",
            rotation="00:00",       # new file every day
            retention="30 days",
            compression="gz",
            format=_json_formatter,
            level=LOG_LEVEL,
            enqueue=True,
        )
    else:
        # Development: colourful, human-readable
        logger.add(
            sys.stderr,
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> – <level>{message}</level>",
            level=LOG_LEVEL,
        )

    logger.info(f"Logger configured | env={ENV} | level={LOG_LEVEL}")
