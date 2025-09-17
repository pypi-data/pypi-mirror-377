
try:
    from opentelemetry.sdk.logs import LogData
except ImportError:
    LogData = None

class CustomLogProcessor:
    """
    A custom OpenTelemetry log processor that applies a standard
    logging.Formatter to the log record's body when available.
    """
    def __init__(self, formatter):
        self.formatter = formatter

    def __call__(self, log_data):
        """
        Best-effort: if log_data has the expected structure, replace body with
        formatted text. Otherwise no-op and return log_data unchanged.
        """
        try:
            log_record = getattr(log_data, "log_record", None)
            if log_record is not None:
                # Some OpenTelemetry versions expose a LogRecord-like object
                formatted = self.formatter.format(log_record)
                # set body if attribute exists
                if hasattr(log_record, "body"):
                    setattr(log_record, "body", formatted)
        except Exception:
            # swallow errors to avoid breaking imports/tests
            pass
        return log_data