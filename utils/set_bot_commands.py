from aiogram import types
from loader import bot


async def set_default_commands():
    """
    Set default commands for the bot using a list of commands from a file.

    Reads command definitions from a file, parses them, and sets them as
    default commands for the bot.

    Args:
        None

    Returns:
        None
    """
    # Read the command definitions from the file
    with open('configs/default_commands.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        commands = [line.strip().split(', ') for line in lines]

    # Create a list of BotCommand objects using the parsed commands
    bot_commands = [types.BotCommand(command=cmd_desc[0], description=cmd_desc[1]) for cmd_desc in commands]

    # Set the parsed commands as default commands for the bot
    await bot.set_my_commands(bot_commands)
