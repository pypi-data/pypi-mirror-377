import requests
import time
import logging
from typing import Callable, Any, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Update:
    """Represents an update from the Lolgram server."""
    def __init__(self, update_id: int, type: str, data: Dict[str, Any]):
        self.update_id = update_id
        self.type = type
        self.data = data

class LolgramInAppBot:
    """
    A Python library for creating and managing in-apps in Lolgram.
    Uses long polling to receive updates from the Lolgram server.
    """
    def __init__(self, api_key: str, base_url: str = "https://f33331a3-cdc1-4d2a-b8a1-71d25d5d423b-00-34uygbkahfgvy.pike.replit.dev"):
        """
        Initialize the bot with an API key and base URL.
        
        Args:
            api_key (str): API key for the in-app, obtained from Lolgram.
            base_url (str): Base URL of the Lolgram server.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.updates_url = f"{self.base_url}/getInAppUpdates"
        self.send_url = f"{self.base_url}/sendInAppAction"
        self.last_update_id = 0
        self.polling = False
        self.handlers = []  # List of (type, handler) tuples

    def add_handler(self, update_type: str, handler: Callable[[Update], Any]):
        """Add a handler for a specific update type (e.g., 'message')."""
        self.handlers.append((update_type, handler))
        logger.info(f"Added handler for update type: {update_type}")

    def send_action(self, action: str, data: Dict[str, Any] = None) -> Dict:
        """
        Send an action/response from the in-app to the server.
        
        Args:
            action (str): The action to perform (e.g., 'send_message').
            data (dict): Additional data for the action.
        
        Returns:
            dict: Server response or None if failed.
        """
        payload = {"apiKey": self.api_key, "action": action}
        if data:
            payload["data"] = data
        try:
            response = requests.post(self.send_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Action sent: {action}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to send action: {e}")
            return None

    def get_updates(self, timeout: int = 20, limit: int = 100) -> List[Update]:
        """
        Fetch updates via long polling.
        
        Args:
            timeout (int): Long polling timeout in seconds.
            limit (int): Maximum number of updates to fetch.
        
        Returns:
            List[Update]: List of updates received.
        """
        params = {
            "apiKey": self.api_key,
            "offset": self.last_update_id,
            "timeout": timeout,
            "limit": limit
        }
        try:
            response = requests.get(self.updates_url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                updates = []
                for u in data.get("result", []):
                    update = Update(u["updateId"], u["type"], u["data"])
                    updates.append(update)
                    self.last_update_id = max(self.last_update_id, u["updateId"])
                return updates
        except requests.RequestException as e:
            logger.error(f"Error fetching updates: {e}")
        return []

    def start_polling(self, interval: float = 0.1):
        """
        Start long polling for updates.
        
        Args:
            interval (float): Delay between polls (in seconds) if no updates.
        """
        self.polling = True
        logger.info("Starting long polling...")
        while self.polling:
            try:
                updates = self.get_updates(timeout=20)
                for update in updates:
                    for utype, handler in self.handlers:
                        if update.type == utype:
                            try:
                                handler(update)
                            except Exception as e:
                                logger.error(f"Handler error: {e}")
                if updates:
                    logger.info(f"Processed {len(updates)} updates")
                time.sleep(interval)
            except KeyboardInterrupt:
                self.stop_polling()
                break
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)  # Wait before retrying on error

    def stop_polling(self):
        """Stop polling."""
        self.polling = False
        logger.info("Polling stopped.")