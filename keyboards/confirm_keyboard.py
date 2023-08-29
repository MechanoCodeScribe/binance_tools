from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder



def confirm_kb() -> ReplyKeyboardMarkup:
    """
    Create a reply keyboard markup with confirmation options.

    Returns a reply keyboard markup containing confirmation and cancel options.

    Returns:
        ReplyKeyboardMarkup: The reply keyboard markup with confirmation options.
    """
    kb = ReplyKeyboardBuilder()  # Create a ReplyKeyboardBuilder instance
    kb.button(text="confirm")     # Add confirm button
    kb.button(text="/cancel")     # Add cancel command button
    kb.adjust(2)                  # Adjust the keyboard layout
    return kb.as_markup(resize_keyboard=True)  # Return the markup with resize_keyboard option