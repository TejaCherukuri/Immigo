import os
import logging

os.makedirs("logs/", exist_ok=True)
logging.basicConfig(
        filename=os.path.join("logs", 'app.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
)