import logging
import os

from helpers.git_pull import git_sync

if not os.path.exists("/app/log"):
    os.mkdir("/app/log")

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("/app/log/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

if __name__ == "__main__":
    logger.info("Hello World!")

    logger.info('Pulling Data')