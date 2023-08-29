from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.my_states import SBuyState
from APIs.api import get_balance, get_symbols
from APIs.trading_view import tw_script
from keyboards.intervals_keyboard import intervals_kb
from keyboards.confirm_keyboard import confirm_kb

router = Router()


@router.message(Command("strong_buy"))
async def get_symb(message: types.Message, state: FSMContext):
    """
    Handle the /strong_buy command to initiate the strong buy process.

    Retrieves the balance information, prompts the user to enter a symbol,
    and sets the state to SBuyState.symbol_input.

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
            await state.set_state(SBuyState.symbol_input)
            await message.answer(
                f"Asset: {item['asset']}\nTotal Balance: {item['total_balance']}\nLocked balance: {item['locked_balance']}\n")
            spot_symbols = get_symbols()
            await state.update_data(spot_symbols=spot_symbols)
            await message.answer("Please enter SYMBOL: ")
    else:
        await message.answer('\nNot enough funds. Please check your spot wallet')


@router.message(SBuyState.symbol_input)
async def get_intervals(message: types.Message, state: FSMContext):
    """
    Handle symbol input and advance to the interval input step.

    Validates the symbol entered by the user and sets the state to SBuyState.interval_input.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user_data = await state.get_data()
    symbol = message.text.upper()
    if symbol in user_data['spot_symbols']:
        ints = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d', '1w', '1mon']
        await state.update_data(symbol=symbol)
        await state.update_data(ints=ints)
        await state.set_state(SBuyState.interval_input)
        await message.answer("Please choose one of available intervals", reply_markup=intervals_kb())
    else:
        await message.answer(text="Incorrect symbol. Please try again ")


@router.message(SBuyState.interval_input)
async def get_qnty(message: types.Message, state: FSMContext):
    """
    Handle interval input and advance to the quantity input step.

    Validates the interval entered by the user and sets the state to SBuyState.qnty_input.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    intrv = message.text
    user_data = await state.get_data()
    if intrv in user_data['ints']:
        await state.update_data(intrv=intrv)
        await state.set_state(SBuyState.qnty_input)
        await message.answer('Please enter amount for trading:', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(text="Incorrect interval. Please try again.")


@router.message(SBuyState.qnty_input, F.text.regexp(r'^\d+$'))
async def get_confrm(message: types.Message, state: FSMContext):
    """
    Handle quantity input and advance to the confirmation step.

    Validates the quantity entered by the user and sets the state to SBuyState.conf_input.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    qnty = message.text
    user_data = await state.get_data()
    await state.update_data(qnty=qnty)
    await message.answer(text="<b>Is that correct? Please check once again:</b>")
    await state.set_state(SBuyState.conf_input)
    await message.answer(f"Symbol: {user_data['symbol']}\nInterval: {user_data['intrv']}\nAmount: {qnty}", reply_markup=confirm_kb())


@router.message(SBuyState.conf_input, F.text == 'confirm')
async def start_trading(message: types.Message, state: FSMContext):
    """
    Start the strong buy trading process.

    Initiates the strong buy trading process and clears the state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user_data = await state.get_data()
    await message.answer(text="Starting..."
                              "\nto stop execution print 'q'", reply_markup=types.ReplyKeyboardRemove())
    await tw_script(message, state, user_data['symbol'], user_data['intrv'], int(user_data['qnty']))
    await state.clear()


@router.message(SBuyState.conf_input, F.text == 'q')
async def stop_running(message: types.Message, state: FSMContext):
    """
    Stops the running strong buy process and clears the state.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await message.answer(text="Execution stopped")
    await state.clear()


@router.message(SBuyState.conf_input)
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


@router.message(SBuyState.qnty_input)
async def amount_chosen_incorrectly(message: types.Message):
    """
    Handle incorrect quantity input.

    Responds to incorrect input during the quantity input step.

    Args:
        message (types.Message): The incoming message object.

    Returns:
        None
    """
    await message.answer(text="Incorrect input. Try again.")


@router.message(F.text)
async def stop_running(message: types.Message):
    """
    Handle unknown commands.

    Responds to unknown commands with a message.

    Args:
        message (types.Message): The incoming message object.

    Returns:
        None
    """
    await message.answer(text="Unknown command")

