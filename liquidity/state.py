

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self):
        self.status = "neutral"  

    def set_status(self, new_status):
        self.status = new_status
        logger.info(f"Status updated to: {self.status}")

    def get_status(self):
        return self.status
