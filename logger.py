import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("myapp.log"),
        logging.StreamHandler(sys.stdout) 
    ]
)

logger = logging.getLogger(__name__)