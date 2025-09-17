import asyncio
import websockets
import json
import logging
from websockets.exceptions import ConnectionClosed, InvalidMessage, WebSocketException

class WebSocketService:
    def __init__(self):
        self.connections = {}  # Active WebSocket connections
        self.subscriptions = {}  # Subscription data for reconnects
        self.reconnect_delay = 5  # Initial delay before reconnecting
        self.max_reconnect_attempts = 10  # Prevent infinite loops
        
    async def connect(self, exchange_name, ws_url, subscription_message, message_handler, auth_message_generator=None):
        """Establish a WebSocket connection, handle messages, and manage reconnects."""
        attempt = 0
        while attempt < self.max_reconnect_attempts:
            try:
                async with websockets.connect(ws_url) as ws:
                    self.connections[exchange_name] = ws
                    self.subscriptions[exchange_name] = (ws_url, subscription_message, message_handler, auth_message_generator)

                    if subscription_message:
                        messages_to_send = subscription_message

                        # If auth_message_generator is provided, regenerate auth message for reconnects
                        if auth_message_generator and attempt > 0:
                            logging.debug(f"[{exchange_name}] Regenerating auth message for reconnect attempt {attempt}")
                            try:
                                fresh_auth_msg, sub_msg = await auth_message_generator()
                                messages_to_send = [fresh_auth_msg, sub_msg]
                                logging.debug(f"[{exchange_name}] Generated fresh auth message")
                            except Exception as gen_error:
                                logging.error(f"[{exchange_name}] Failed to generate fresh auth: {gen_error}")
                                # Fall back to original messages
                                messages_to_send = subscription_message

                        # Handle both single message and list of messages (for auth + subscribe)
                        if isinstance(messages_to_send, list):
                            for msg in messages_to_send:
                                await ws.send(json.dumps(msg))
                                logging.debug(f"[{exchange_name}] Sent: {msg.get('op', 'unknown')}")
                        else:
                            await ws.send(json.dumps(messages_to_send))

                    logging.info(f"[{exchange_name}] Connected to WebSocket: {ws_url}")

                    async for message in ws:
                        await self._process_message(exchange_name, message, message_handler)
            
            except (ConnectionClosed, asyncio.TimeoutError, OSError, WebSocketException) as e:
                self._handle_error(exchange_name, e)
            except Exception as e:
                logging.error(f"[{exchange_name}] Unexpected error: {e}")
            
            attempt += 1
            await asyncio.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, 60)  # Exponential backoff
        
        logging.error(f"[{exchange_name}] Max reconnect attempts reached. Stopping retries.")

    async def _process_message(self, exchange_name, message, message_handler):
        """Process incoming WebSocket messages."""
        try:
            parsed_message = json.loads(message)
            await message_handler(exchange_name, parsed_message)
        except json.JSONDecodeError as e:
            logging.error(f"[{exchange_name}] JSON Decode Error: {e} - Message: {message}")
        except InvalidMessage as e:
            logging.error(f"[{exchange_name}] Invalid WebSocket Message: {e}")

    def _handle_error(self, exchange_name, error):
        """Handles WebSocket errors with appropriate logging."""
        error_type = type(error).__name__
        logging.warning(f"[{exchange_name}] {error_type}: {error}. Retrying in {self.reconnect_delay} sec...")

    async def subscribe(self, exchange_name, ws_url, subscription_message, message_handler, auth_message_generator=None):
        """Start a WebSocket connection asynchronously."""
        # Create task but don't await - we need this to run in background
        task = asyncio.create_task(self.connect(exchange_name, ws_url, subscription_message, message_handler, auth_message_generator))
        # Give it a moment to establish connection and send initial messages
        await asyncio.sleep(1)
        return task

    async def disconnect(self, exchange_name):
        """Close a WebSocket connection gracefully."""
        if exchange_name in self.connections:
            try:
                await self.connections[exchange_name].close()
                logging.info(f"[{exchange_name}] Disconnected from WebSocket.")
            except Exception as e:
                logging.error(f"[{exchange_name}] Error while disconnecting: {e}")
            finally:
                del self.connections[exchange_name]

    async def send_message(self, exchange_name, message):
        """Send a message to an active WebSocket connection."""
        if exchange_name in self.connections:
            try:
                ws = self.connections[exchange_name]
                await ws.send(json.dumps(message))
                logging.debug(f"[{exchange_name}] Sent message: {message.get('op', 'unknown')}")
                return True
            except Exception as e:
                logging.error(f"[{exchange_name}] Failed to send message: {e}")
                return False
        else:
            logging.warning(f"[{exchange_name}] No active connection to send message")
            return False

    async def restart_connection(self, exchange_name):
        """Manually restart a WebSocket connection."""
        if exchange_name in self.subscriptions:
            subscription_data = self.subscriptions[exchange_name]
            if len(subscription_data) == 4:
                ws_url, subscription_message, message_handler, auth_message_generator = subscription_data
            else:
                ws_url, subscription_message, message_handler = subscription_data
                auth_message_generator = None

            logging.info(f"[{exchange_name}] Restarting WebSocket connection...")
            await self.subscribe(exchange_name, ws_url, subscription_message, message_handler, auth_message_generator)
