from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()




@router.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    """
    Handle the /start command.

    Responds to the start command, clears the current state, and provides a welcome message.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await message.answer_sticker('CAACAgIAAxkBAAIDf2TnHmtOXKiPqLobWNMHYjzhV5L5AAIzDQACQImhSq1rDlQ0SeA5MAQ')
    await message.answer("<b>Welcome to Brian's trading tool!</b>\n"
                         "\n<b>Available commands:</b>\n"
                         "\n/start - Return to beginning\n"
                         "\n/strong_buy - Execute the trading strategy based on 'STRONG BUY' and 'STRONG SELL' signals from TradingView\n"
                         "\n/my_strategy - Spot trading using previously configured custom strategy\n"
                         "\n/cancel - Use it to terminate any process", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(Command('cancel'))
async def cancel_command(message: types.Message, state: FSMContext):
    """
    Handle the /cancel command.

    Responds to the cancel command and clears the current state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await message.answer('Current process is terminated', reply_markup=types.ReplyKeyboardRemove())
    await state.clear()