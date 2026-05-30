import logging


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=_normalize_log_level(level),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _normalize_log_level(level: str) -> int:
    return getattr(logging, level.upper(), logging.INFO)
