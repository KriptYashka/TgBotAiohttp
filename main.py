import asyncio
import os

import aiohttp
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.environ.get("TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
POLL_TIMEOUT = 30


class TelegramBot:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.offset = 0

    async def close(self):
        await self.session.close()

    async def get_updates(self):
        url = API_URL + "getUpdates"
        params = {
            "timeout": POLL_TIMEOUT,
            "offset": self.offset + 1 if self.offset else None
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", [])
                logger.error(f"Ошибка HTTP {response.status}: {await response.text()}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при получении обновлений: {e}", exc_info=True)
            return []

    async def send_message(self, chat_id, text):
        url = API_URL + "sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Ошибка при отправке: {await response.text()}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")

    async def process_message(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/start"):
            await self.send_message(chat_id, "Hello World! Я бот на asyncio + aiohttp.")
        else:
            await self.send_message(chat_id, "Hello World!")

    async def run(self):
        logger.info("Бот запущен...")
        try:
            while True:
                updates = await self.get_updates()
                for update in updates:
                    self.offset = update["update_id"]  # Обновляем offset
                    if "message" in update:
                        await self.process_message(update["message"])
        except asyncio.CancelledError:
            logger.info("Бот остановлен.")
        finally:
            await self.close()


async def main():
    bot = TelegramBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Завершение работы по Ctrl+C...")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
