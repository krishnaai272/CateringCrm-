import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def log_spam_attempt(email: str):
    logger.warning(f"Spam detected from email: {email}")


def log_lead_created(email: str):
    logger.info(f"Lead created successfully for: {email}")