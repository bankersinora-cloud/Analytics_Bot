import logging
import os
import sys, warnings

def create_logs(agent_name):
    warnings.filterwarnings("ignore")
    os.makedirs("logs", exist_ok=True)
    log_file_path = os.path.join("logs", f"{agent_name}.log")

    logger = logging.getLogger("TAABI")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger