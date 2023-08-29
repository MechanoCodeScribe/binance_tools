from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.my_states import AmountState
from APIs.api import get_balance, strategy
from loader import client
from keyboards.confirm_keyboard import confirm_kb

router = Router()


@router.message(Command("my_strategy"))
async def show_balance(message: types.Message, state: FSMContext):
    """
    Handle the /my_strategy command to initiate the trading strategy.

    Retrieves the balance information, prompts the user to enter a USDT amount for trading,
    and sets the state to AmountState.amount_input.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    balance = get_balance()
    if balance:
        await message.answer("<b>Your current assets:</b>")
        for item in balance:
            await message.answer(
                f"\nAsset: {item['asset']}\nTotal Balance: {item['total_balance']}\nLocked balance: {item['locked_balance']}\n")
            await message.answer("Enter USDT amount for trading: ")
            await state.set_state(AmountState.amount_input)
    else:
        await message.answer('\nNot enough funds. Please check your spot wallet')


@router.message(AmountState.amount_input, F.text.regexp(r'^\d+$'))
async def process_amount_input(message: types.Message, state: FSMContext):
    """
    Process the user's input for the trading amount.

    Validates and stores the user's chosen trading amount and advances to the confirmation state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await state.update_data(chosen_amount=message.text)
    await message.answer(text="<b>Is that correct? Please check once again:</b>")
    user_data = await state.get_data()
    await message.answer(f"Chosen amount: {user_data['chosen_amount']} USDT", reply_markup=confirm_kb())
    await state.set_state(AmountState.confirm_input)


@router.message(AmountState.confirm_input, F.text == 'confirm')
async def start_trading(message: types.Message, state: FSMContext):
    """
    Start the trading strategy with the chosen amount.

    Initiates the trading strategy with the user's chosen amount and clears the state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await message.answer(text="Starting..."
                              "\nto stop execution print 'q'", reply_markup=types.ReplyKeyboardRemove())
    user_data = await state.get_data()
    await strategy(message, state, int(user_data['chosen_amount']))
    await state.clear()


@router.message(AmountState.confirm_input, F.text == 'q')
async def stop_running(message: types.Message, state: FSMContext):
    """
    Stops the running strategy and clears the state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await message.answer(text="Execution stopped")
    await state.clear()


@router.message(AmountState.confirm_input)
async def confirmation_chosen_incorrectly(message: types.Message):
    """
    Handle incorrect confirmation input.

    Responds to incorrect input during the confirmation step.

    Args:
        message (types.Message): The incoming message object.

    Returns:
        None
    """
    await message.answer(text="Incorrect input.")


@router.message(AmountState.amount_input)
async def amount_chosen_incorrectly(message: types.Message):
    """
    Handle incorrect amount input.

    Responds to incorrect input during the amount input step.

    Args:
        message (types.Message): The incoming message object.

    Returns:
        None
    """
    await message.answer(text="Incorrect input. Please try again")