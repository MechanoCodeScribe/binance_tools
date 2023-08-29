from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder



def intervals_kb() -> ReplyKeyboardMarkup:
    """
    Create a reply keyboard markup with intervals.

    Returns a reply keyboard markup containing interval options for user selection.

    Returns:
        ReplyKeyboardMarkup: The reply keyboard markup with interval options.
    """
    kb = ReplyKeyboardBuilder()  # Create a ReplyKeyboardBuilder instance
    kb.button(text="1m")          # Add interval buttons
    kb.button(text="5m")
    kb.button(text="15m")
    kb.button(text="30m")
    kb.button(text="1h")
    kb.button(text="2h")
    kb.button(text="4h")
    kb.button(text="1d")
    kb.button(text="1w")
    kb.button(text="1mon")
    kb.adjust(5)                  # Adjust the keyboard layout
    return kb.as_markup(resize_keyboard=True)  # Return the markup with resize_keyboard option