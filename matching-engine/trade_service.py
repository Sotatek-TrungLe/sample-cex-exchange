import requests
from config import Config
from logger import logger

def send_trade_to_balance_service(trade):
    """Sends trade data to the Balance Service to adjust balances."""
    try:
        response = requests.post(Config.BALANCE_SERVICE_API, json=trade)
        response.raise_for_status()
        logger.info(f"Trade sent to Balance Service: {trade}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send trade to Balance Service: {e}")
