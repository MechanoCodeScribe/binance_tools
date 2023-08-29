import asyncio
import logging
import sys
from loader import bot
from handlers import start, strategy, strong_buy
from utils.set_bot_commands import set_default_commands
from aiogram import Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage


async def main() -> None:
    """
    The main entry point for the bot's execution.

    This function initializes the dispatcher with memory storage, sets default commands,
    includes routers for different functionalities, deletes any pending webhook updates,
    and starts polling for updates from the bot.

    Args:
        None

    Returns:
        None
    """

    # Create a Dispatcher instance with MemoryStorage
    dp = Dispatcher(storage=MemoryStorage())

    # Set default commands for the bot
    await set_default_commands()

    # Include routers for different parts of the bot's functionality
    dp.include_router(start.router)
    dp.include_router(strategy.router)
    dp.include_router(strong_buy.router)

    # Delete any pending updates from the webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # Start polling for updates using the dispatcher
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    The main entry point of the script.

    Sets up logging configuration, initializes the event loop, and starts
    the main function asynchronously.

    Args:
        None

    Returns:
        None
    """

    # Configure logging to display INFO level logs to the standard output stream
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Run the main function using the asyncio event loop
    asyncio.run(main())

