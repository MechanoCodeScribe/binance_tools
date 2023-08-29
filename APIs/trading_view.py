from tradingview_ta import TA_Handler, Interval, Exchange, TradingView
from APIs.api import place_order
from aiogram.fsm.context import FSMContext
from states.my_states import SBuyState

import asyncio


def get_data(symbol, interval):
    """
    Get trading data and analysis for a specific symbol and interval.

    Retrieves trading data and analysis for the provided symbol and interval.

    Args:
        symbol (str): The trading symbol.
        interval (str): The trading interval.

    Returns:
        dict: Analysis summary for the provided symbol and interval.
    """
    if interval == '1m':
        interval = Interval.INTERVAL_1_MINUTE
    elif interval == '5m':
        interval = Interval.INTERVAL_5_MINUTES
    elif interval == '15m':
        interval = Interval.INTERVAL_15_MINUTES
    elif interval == '30m':
        interval = Interval.INTERVAL_30_MINUTES
    elif interval == '1h':
        interval = Interval.INTERVAL_1_HOUR
    elif interval == '2h':
        interval = Interval.INTERVAL_2_HOURS
    elif interval == '4h':
        interval = Interval.INTERVAL_4_HOURS
    elif interval == '1d':
        interval = Interval.INTERVAL_1_DAY
    elif interval == '1w':
        interval = Interval.INTERVAL_1_WEEK
    elif interval == '1mon':
        interval = Interval.INTERVAL_1_MONTH

    output = TA_Handler(symbol=symbol,
                        screener='crypto',
                        exchange='Binance',
                        interval=interval
                        )

    # Get the summary of signals from all major indicators
    activity = output.get_analysis().summary
    return activity


async def tw_script(message, state, symbol, interval, amt):
    """
    Execute the trading strategy based on symbol, interval, and amount.

    Executes the trading strategy by continuously analyzing the provided symbol and interval,
    and placing buy/sell orders according to the strategy's recommendations.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context.
        symbol (str): The trading symbol.
        interval (str): The trading interval.
        amt (int): The trading amount.

    Returns:
        None
    """
    buy = False
    sell = False
    current_state = await state.get_state()

    while current_state == SBuyState.conf_input:

        data = get_data(symbol, interval)
        await message.answer(f"<b>Recommendation: {data['RECOMMENDATION']}</b>"
                             f"\nBuy: {data['BUY']}"
                             f"\nSell {data['SELL']}")

        if data['RECOMMENDATION'] == 'STRONG_BUY' and not buy:
            await message.answer('PLACING  !!!___BUY___!!!  ORDER')
            result = place_order('BUY', symbol, amt)
            print(str(result))
            buy = True
            sell = False

        # When recommendation is STRONG_SELL and we haven't sold yet
        if data['RECOMMENDATION'] == 'STRONG_SELL' and not sell:
            await message.answer('PLACING  !!!___SELL___!!!  ORDER')
            result = place_order('SELL', symbol, amt)
            await message.answer(str(result))
            buy = False
            sell = True

        await asyncio.sleep(1)
        current_state = await state.get_state()