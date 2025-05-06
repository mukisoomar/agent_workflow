import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename='logs/agent.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    return logging.getLogger(name)
