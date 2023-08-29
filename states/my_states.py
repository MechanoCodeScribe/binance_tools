from aiogram.fsm.state import StatesGroup, State

class AmountState(StatesGroup):
    amount_input = State()
    confirm_input = State()
    check_input = State()

class SBuyState(StatesGroup):
    symbol_input = State()
    interval_input = State()
    qnty_input = State()
    wrong_amt = State()
    conf_input = State()

class AmountState(StatesGroup):
    """
    Represents different states of the amount input process.

    This class defines states related to entering and confirming amounts.

    States:
        - amount_input: State for entering an amount.
        - confirm_input: State for confirming the entered amount.
        - check_input: State for checking the entered amount.

    """

    amount_input = State()
    confirm_input = State()
    check_input = State()

class SBuyState(StatesGroup):
    """
    Represents different states of the strong buy input process.

    This class defines states related to entering various inputs for a strong buy.

    States:
        - symbol_input: State for entering a symbol.
        - interval_input: State for entering an interval.
        - qnty_input: State for entering a quantity.
        - wrong_amt: State for handling wrong amount input.
        - conf_input: State for confirming the input.

    """

    symbol_input = State()
    interval_input = State()
    qnty_input = State()
    wrong_amt = State()
    conf_input = State()


