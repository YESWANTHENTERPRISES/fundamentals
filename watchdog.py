"""
Zero-Prompt Asynchronous Background Economic Event Watchdog
Monitors armed high-impact events and polls every 3 seconds around release time.
Automatically triggers Gemini impact analysis and pushes instant alerts to Telegram.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Set, Any, Optional
from calendar_service import calendar_service, EconomicEvent
from microstructure_service import get_microstructure_data
from gemini_engine import generate_post_news_impact
from config import DOMAIN_CONFIGS

logger = logging.getLogger("WatchdogManager")


class WatchdogManager:
    def __init__(self):
        # Mapping: event_id -> {"event": EconomicEvent, "domain_id": str, "chats": Set[int]}
        self.armed_events: Dict[str, Dict[str, Any]] = {}
        # Mapping: domain_id -> Telegram Bot instance
        self.bot_instances: Dict[str, Any] = {}
        self.is_running = False
        self._loop_task: Optional[asyncio.Task] = None

    def register_bot_instance(self, domain_id: str, bot: Any):
        """Registers the Telegram Bot instance for a domain."""
        self.bot_instances[domain_id] = bot
        logger.info(f"Registered Telegram Bot instance for domain '{domain_id}'")

    def arm_event(self, event: EconomicEvent, domain_id: str, chat_id: int):
        """Arms a background watchdog for an event and subscribes a chat_id."""
        if event.event_id not in self.armed_events:
            self.armed_events[event.event_id] = {
                "event": event,
                "domain_id": domain_id,
                "chats": set(),
                "polling_active": False,
                "armed_at": datetime.now(timezone.utc),
            }
        self.armed_events[event.event_id]["chats"].add(chat_id)
        logger.info(f"Armed watchdog for event '{event.title}' (ID: {event.event_id}) for chat {chat_id} in domain '{domain_id}'. Total subscribers: {len(self.armed_events[event.event_id]['chats'])}")

    def get_armed_count(self) -> int:
        return len(self.armed_events)

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "total_armed_events": len(self.armed_events),
            "events": [
                {
                    "id": eid,
                    "title": data["event"].title,
                    "domain": data["domain_id"],
                    "subscribers": len(data["chats"]),
                    "release_time": data["event"].scheduled_time.isoformat(),
                    "countdown": data["event"].countdown_str()
                }
                for eid, data in self.armed_events.items()
            ]
        }

    async def start(self):
        """Starts the background watchdog polling loop."""
        if self.is_running:
            return
        self.is_running = True
        self._loop_task = asyncio.create_task(self._watchdog_loop())
        logger.info("Background 24/7 Watchdog Manager loop started.")

    async def stop(self):
        """Stops the watchdog loop."""
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        logger.info("Background Watchdog Manager loop stopped.")

    async def _watchdog_loop(self):
        """Main polling loop running every 3 seconds."""
        while self.is_running:
            try:
                now = datetime.now(timezone.utc)
                events_to_trigger = []

                for event_id, item in list(self.armed_events.items()):
                    event: EconomicEvent = item["event"]
                    domain_id: str = item["domain_id"]

                    # If release time is within 30 seconds or has passed
                    time_diff = (event.scheduled_time - now).total_seconds()
                    
                    # Start polling if release is imminent (<= 15 seconds) or in the past
                    if time_diff <= 15:
                        actual_val = await calendar_service.check_event_released(event)
                        if actual_val:
                            events_to_trigger.append((event_id, actual_val))

                # Trigger any released events
                for event_id, actual_val in events_to_trigger:
                    await self._execute_release_alert(event_id, actual_val)

            except Exception as e:
                logger.error(f"Error in watchdog loop: {e}", exc_info=True)

            await asyncio.sleep(3)  # Poll every 3 seconds

    async def _execute_release_alert(self, event_id: str, actual_value: str):
        """Executes Phase B: generates Gemini impact and pushes alerts to Telegram."""
        if event_id not in self.armed_events:
            return

        item = self.armed_events.pop(event_id)
        event: EconomicEvent = item["event"]
        domain_id: str = item["domain_id"]
        subscribers: Set[int] = item["chats"]

        config = DOMAIN_CONFIGS.get(domain_id)
        bot_name = config.bot_name if config else "INSTITUTIONAL BOT"
        bot = self.bot_instances.get(domain_id)

        micro_data = get_microstructure_data(domain_id)

        # Generate the exact Post-News Alert via Gemini
        alert_text = await generate_post_news_impact(
            domain_id=domain_id,
            bot_name=bot_name,
            event_title=event.title,
            actual=actual_value,
            forecast=event.forecast,
            previous=event.previous,
            micro_data=micro_data,
        )

        logger.info(f"Broadcasting Automatic Post-News Alert for '{event.title}' to {len(subscribers)} chats.")

        # Push to each subscribed chat
        for chat_id in subscribers:
            try:
                if bot:
                    await bot.send_message(chat_id=chat_id, text=alert_text, parse_mode=None)
                else:
                    logger.warning(f"No bot instance registered for domain '{domain_id}' to send to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to push alert to chat {chat_id}: {e}")

    async def trigger_manual_alert(self, domain_id: str, chat_id: int, custom_actual: str = "0.1%"):
        """
        Manually triggers a Phase B alert for testing or instant demonstration.
        Ensures the user can witness zero-prompt behavior anytime.
        """
        config = DOMAIN_CONFIGS.get(domain_id)
        bot_name = config.bot_name if config else "INSTITUTIONAL BOT"
        bot = self.bot_instances.get(domain_id)
        micro_data = get_microstructure_data(domain_id)

        # Grounded event title for testing
        if domain_id == "commodities":
            event_title = "US Core CPI m/m"
            forecast = "0.3%"
            previous = "0.2%"
        elif domain_id == "forex":
            event_title = "US Non-Farm Payrolls (NFP)"
            forecast = "140K"
            previous = "142K"
            custom_actual = "110K"
        else:
            event_title = "ISM Services PMI"
            forecast = "53.8"
            previous = "51.5"
            custom_actual = "56.2"

        alert_text = await generate_post_news_impact(
            domain_id=domain_id,
            bot_name=bot_name,
            event_title=event_title,
            actual=custom_actual,
            forecast=forecast,
            previous=previous,
            micro_data=micro_data,
        )

        if bot:
            await bot.send_message(chat_id=chat_id, text=alert_text, parse_mode=None)
        return alert_text


# Global singleton instance
watchdog_manager = WatchdogManager()
