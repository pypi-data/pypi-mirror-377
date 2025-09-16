import logging
import json
import sys
from datetime import datetime

# ---- Custom SUCCESS level ----
SUCCESS_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success

# ---- JSON Formatter ----
class JsonFormatter(logging.Formatter):
    """
    Output each log record as a single-line JSON object.
    Extra fields passed as kwargs to logger.<level>() will be included.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "message": record.getMessage(),
        }

        # Merge any `extra` kwargs from logger calls
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        # Handle exceptions properly
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)

# ---- Configure root handler ----
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("media_manipulator_service")
logger.setLevel(logging.INFO)      # Adjust INFO/ERROR as needed in prod
logger.addHandler(handler)
logger.propagate = False
