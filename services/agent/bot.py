# 1st party
import sys
import asyncio
import logging

# internal lib
from src.config import config

# from src.react_agent import ReActAgent
from src.react_agent import ReActAgent
from src.llm.factory import llm
from src.tools import tools

# 3rd party
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
# from llama_index.core.workflow import Context
# Bot token can be obtained via https://t.me/BotFather
# All handlers should be attached to the Router (or Dispatcher)


agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)

# ctx = Context(agent)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    Args:
        message (Message): Telegram aiogram Message object. Expected "/start"
    Return:
        None
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    Args:
        message (Message): Telegram aiogram Message object.
    Return:
        None
    """
    try:
        response = await agent.run(input=message.text)
        # logger.info(response)
        # Send a copy of the received message
        await message.answer(response["response"])
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.api_key_bot_telegram,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
