from binance.exceptions import BinanceAPIException
from loader import client
import pandas as pd
import time
from states.my_states import AmountState
import asyncio


def place_order(order_type, symbol, amt):
    """
        Place a trading order.

        Places a trading order of the specified type (BUY or SELL) for the given symbol and amount.

        Args:
            order_type (str): The type of order, either 'BUY' or 'SELL'.
            symbol (str): The trading symbol.
            amt (float): The trading amount.

        Returns:
            dict or str: The order details if successful, or an error message if an exception occurs.
    """
    try:
        order = client.create_order(symbol=symbol, side=order_type, type='MARKET', quantity=amt)
        return order
    except BinanceAPIException as e:
        error_message = f"An error occurred while creating the order: {e.message}"
        return error_message


def get_symbols():
    """
        Get a list of tradable spot symbols.

        Retrieves a list of tradable spot symbols from the exchange information.

        Returns:
            list: A list of  spot symbols.
    """
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']
    spot_symbols = [symbol['symbol'] for symbol in symbols if 'SPOT' in symbol['permissions']]
    return spot_symbols


def get_balance():
    """
        Get balance information for each tradable asset.

        Retrieves balance information for each tradable asset, including total balance and locked balance.

        Returns:
            list: A list of dictionaries containing balance data for each asset.
                  Each dictionary contains keys 'asset', 'total_balance', and 'locked_balance'.
    """

    account_info = client.get_account()

    balance_data = []

    # Prints balance for each coin
    for balance in account_info['balances']:
        asset = balance['asset']
        free_balance = float(balance['free'])
        locked_balance = float(balance['locked'])
        total_balance = free_balance + locked_balance
        if total_balance > 0:
            asset_data = {
                'asset': asset,
                'total_balance': total_balance,
                'locked_balance': locked_balance
            }
            balance_data.append(asset_data)
    return balance_data


def top_coin():
    """
        Get the top-performing coin trading against USDT.

        Retrieves the top-performing coin that is trading against USDT based on the highest price change percent.

        Returns:
            str: The symbol of the top-performing coin.
    """
    # Fetch all tickers from the client
    all_tickers = pd.DataFrame(client.get_ticker())
    # Filter tickers that are trading against USDT
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    # Remove coins with symbols containing 'UP' or 'DOWN'
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    # Sort by price change percent to find the top coin
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin


def last_data(symbol, interval, lookback):
    """
        Get the last historical data for a symbol within a specified lookback period.

        Retrieves the last historical data for a given symbol and interval within the specified lookback period.

        Args:
            symbol (str): The trading symbol.
            interval (str): The trading interval.
            lookback (str): The lookback period in minutes.

        Returns:
            pandas.DataFrame: Historical data frame containing columns for Time, Open, High, Low, Close, and Volume.
    """
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    # Select only the first 6 columns of data
    frame = frame.iloc[:, :6]
    # Assign column names
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # Sort by time and convert time to human-readable format
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    # Convert string data to numeric values for comparison
    frame = frame.astype(float)
    return frame


# функция осуществления торговли
# buy_amt - тот объем на который му будем заходить в сделку
async def strategy(message, state, buy_amt, SL=0.985, Target=1.02, open_position=False):
    """
        Execute the trading strategy based on specified parameters.

        Executes the trading strategy by analyzing the most active coin, calculating trade quantity,
        and placing buy/sell orders according to the strategy's recommendations.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The state context.
            buy_amt (float): The amount for trading.
            SL (float, optional): The stop-loss factor. Defaults to 0.985.
            Target (float, optional): The take-profit factor. Defaults to 1.02.
            open_position (bool, optional): Indicator for open position. Defaults to False.

        Returns:
            None
    """
    current_state = await state.get_state()
    if current_state == AmountState.confirm_input:
        try:
            # Get the most active coin
            asset = top_coin()
            # Check growth using one-minute candles for the last 120 minutes
            df = last_data(asset, '1m', '120')
            await message.answer(f'Most active coin: {asset}')
        except:
            await message.answer('Failed to get data. Will try again in 1 minute')
            await asyncio.sleep(61)
            asset = top_coin()
            df = last_data(asset, '1m', '120')
            await message.answer(f'Most active coin: {asset}')
        # Calculate trade quantity based on buy amount and last closing price
        qty = round(buy_amt / df.Close.iloc[-1], 1)

        # Check if the price change percent is significant
        if ((df.Close.pct_change() + 1).cumprod()).iloc[-1] > 100000:
            await message.answer(f'Creating "BUY" order. Ammount: {qty}\nLast kline close price {df.Close.iloc[-1]}')

            try:
                order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity=qty)
            except BinanceAPIException as e:
                error_message = f"An error occurred while creating the order: {e.message}"
                await message.answer(error_message)
                return
            buyprice = float(order['fills'][0]['price'])
            await message.answer('Order confirmed!')

            open_position = True

            while open_position and current_state == AmountState.confirm_input:

                try:
                    await message.answer('Checking prices...')
                    await asyncio.sleep(3)
                    df = last_data(asset, '1m', '2')
                except:
                    await message.answer('Failed to get data. Will continue selling in 1 minute')
                    time.sleep(61)
                    df = last_data(asset, '1m', '2')

                await message.answer(f'Price ' + str(df.Close[-1]))
                await message.answer(f'Target price ' + str(buyprice * Target))
                await message.answer(f'Stop loss price ' + str(buyprice * SL))

                if df.Close[-1] <= buyprice * SL or df.Close[-1 >= buyprice * Target]:
                    await message.answer(f'Creating "SELL" order. Ammount: {qty}\nBuy price: {buyprice}')
                    try:
                        order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity=qty)
                        await message.answer('SELL order confirmed!')
                        break
                    except BinanceAPIException as e:
                        error_message = f"An error occurred while creating the order: {e.message}"
                        await message.answer(error_message)
                        break

        else:
            await message.answer('No suitable asset found.\nNext try in 20 sec... ')
            await asyncio.sleep(20)
            await strategy(message, state, buy_amt)
