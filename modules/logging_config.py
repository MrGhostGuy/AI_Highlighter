
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO", log_file: str = "ai_highlighter.log", base_dir: str = "."):
    log_path = os.path.join(base_dir, "logs")
    os.makedirs(log_path, exist_ok=True)
    full_path = os.path.join(log_path, log_file)
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh = RotatingFileHandler(full_path, maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    ch.setFormatter(fmt)
    root.addHandler(ch)
    logging.info(f"Logging initialized: level={log_level}, file={full_path}")
    return root

class PipelineLogger:
    def __init__(self, module_name: str):
        self.logger = logging.getLogger(module_name)
        self.module_name = module_name
        self.timings = {}

    def start_timer(self, operation: str):
        self.timings[operation] = datetime.now()
        self.logger.info(f"[START] {operation}")

    def end_timer(self, operation: str):
        if operation in self.timings:
            elapsed = (datetime.now() - self.timings[operation]).total_seconds()
            self.logger.info(f"[END] {operation} completed in {elapsed:.2f}s")
            del self.timings[operation]
            return elapsed
        return 0.0

    def log_clip_event(self, clip_id: str, event: str, details: dict = None):
        msg = f"[CLIP:{clip_id}] {event}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)

    def log_error(self, operation: str, error: Exception):
        self.logger.error(f"[ERROR] {operation}: {type(error).__name__}: {error}")

    def log_metric(self, metric_name: str, value: float):
        self.logger.info(f"[METRIC] {metric_name}={value:.4f}")
