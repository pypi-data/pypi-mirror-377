import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt
from dataclasses import dataclass
from scipy.optimize import minimize
pd.set_option('display.float_format', '{:,.4f}'.format)



def var_stocks(data: pd.DataFrame, n_stocks: list, conf: int | float, long: bool, stocks: list) -> pd.DataFrame:
    """
    Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of stocks.
    
    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    n_stocks : list
        Number of stocks per ticker.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions
    stocks : list
        A list of column names representing the stocks to be included in the portfolio.
    Returns:
    -----------
    var_stocks_df : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.

    Notes: n_stocks and stocks must coincide in lenght and order.
    """


    data = data.sort_index()
    data = data[stocks]
    rt = data.pct_change().dropna()
    stock_value = n_stocks * data.iloc[-1]
    portfolio_value = stock_value.sum()
    w = stock_value / portfolio_value
    portfolio_return = np.dot(w, rt.T)

    var_pct = np.percentile(portfolio_return, 100-conf) if long else np.percentile(portfolio_return, conf)
    cvar_pct = np.abs(portfolio_return[portfolio_return < var_pct].mean()) if long else portfolio_return[portfolio_return > var_pct].mean()

    var_cash, cvar_cash = np.abs(portfolio_value * var_pct), portfolio_value * cvar_pct

    var_stocks_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentaje": [np.abs(var_pct), cvar_pct],
        "cash": [var_cash, cvar_cash]
    })

    return var_stocks_df



def var_forex(data: pd.DataFrame, positions: list, conf: int | float, long: bool, currencies: list) -> pd.DataFrame:
    """
    Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of currencies.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical exchange rates, indexed by date.
    positions : list
        A list of positions for each currency.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions
    currencies : list
        A list of column names representing the currencies to be included in the portfolio.
    
    Returns:
    -----------
    var_df : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.
    
    Notes: n_stocks and stocks must coincide in lenght and order.
    """

    data = data.sort_index()
    data = data[currencies]
    port = data * positions
    port['total'] = port.sum(axis=1)
    portfolio_return = port['total'].pct_change().dropna()

    var_porcentual = np.percentile(portfolio_return, 100-conf) if long else np.percentile(portfolio_return, conf)
    cvar_porcentual = np.abs(portfolio_return[portfolio_return < var_porcentual].mean()) if long else portfolio_return[portfolio_return > var_porcentual].mean()

    var_cash, cvar_cash = np.abs(port['total'].iloc[-1] * var_porcentual), port['total'].iloc[-1] * cvar_porcentual

    var_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentual": [np.abs(var_porcentual), cvar_porcentual],
        "Cash": [var_cash, cvar_cash]
    })

    return var_df



def rebalance_stocks(w_original: list, target_weights: list, data: pd.DataFrame, stocks: list, portfolio_value: float) -> pd.DataFrame:
    """
    Rebalance a portfolio of stocks to achieve target weights.

    Parameters
    -----------
    w_original : list
        The original weights of the portfolio.
    target_weights : list
        The target weights for the portfolio.
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    stocks : list
        A list of column names representing the stocks to be included in the portfolio.
    portfolio_value : float
        The total value of the portfolio.

    Returns:
    -----------
    w_df : pd.DataFrame

        A DataFrame containing the original and target weights, as well as the number of shares to buy/sell.
    """

    data = data.sort_index()
    data = data[stocks]
    w_df = pd.DataFrame({
    "Peso Original": w_original,
    "Peso Óptimo": target_weights,
    "Acciones (C/V)" : np.floor((target_weights-w_original) * portfolio_value / data.iloc[-1])
    })
    return w_df.T



def get_data(stocks: str | list, start_date: str, end_date: str, type: str = 'Close'):
    """
    A function to download stock data from Yahoo Finance.

    Parameters
    -----------
    stocks : str | list
        The stock tickers to download.
    start_date : str
        The start date for the data.
    end_date : str
        The end date for the data.
    type : str
        The type of data to download (e.g., 'Close', 'Open', 'High', 'Low', 'Adj Close', 'Volume').

    Returns:
    -----------
    data : DataFrame

        A DataFrame containing the stock data.
    """

    data=yf.download(stocks, start=start_date, end=end_date)[type][stocks]
    return data



def var_weights(data: pd.DataFrame, weights: list | np.ndarray, conf: int | float) -> float:
    """
    A function to calculate the Value at Risk (VaR) for a portfolio of stocks.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    weights : list | np.ndarray
        A list of weights for the portfolio.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    
    Returns:
    -----------
    var : float

        The VaR value for the portfolio.
    """

    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    return np.abs(np.percentile(portfolio_returns, 100-conf))


def cvar_weights(data: pd.DataFrame, weights: list | np.ndarray, conf: int | float) -> float:
    """
    A function to calculate the Conditional Value at Risk (CVaR) for a portfolio of stocks.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    weights : list | np.ndarray
        A list of weights for the portfolio.
    conf : int | float
        The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

    Returns:
    -----------
    cvar_pct : float

        The CVaR value for the portfolio.
    """

    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    var = np.percentile(portfolio_returns, 100-conf)
    cvar_pct = np.abs(portfolio_returns[portfolio_returns < var].mean())
    return cvar_pct



def opt_sharpe(returns, rf):

    mu = (returns.mean() * 252).values
    sigma = returns.cov().values
    n_assets = len(mu)

    # Función para minimizar (-Sharpe Ratio)
    def neg_sharpe_ratio(w, mu, sigma, rf):
        port_return = np.dot(w, mu)
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w))) * np.sqrt(252)
        sharpe_ratio = (port_return - rf) / port_vol
        return -sharpe_ratio
    
    # Restricciones: Suma de pesos = 1
    constraints = ({
        'type': 'eq',
        'fun': lambda w: np.sum(w) - 1
    })

    # Límites: Pesos entre 0 y 1 (no posiciones cortas)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Pesos iniciales (distribuidos uniformemente)
    w0 = np.array([1 / n_assets] * n_assets)

    # Optimización
    result = minimize(neg_sharpe_ratio, 
            w0, 
            args=(mu, sigma, rf), 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints)
    
    # Resultados
    w_opt_sharpe = result.x

    return w_opt_sharpe



def min_variance(returns: pd.DataFrame) -> np.array:
    """
    A function to calculate the minimum variance portfolio.

    Parameters
    -----------
    returns : pd.DataFrame
        A DataFrame containing the returns of the assets in the portfolio.

    Returns:
    -----------
    min_var_weights : np.array

        An array containing the weights of the minimum variance portfolio.
    """

    mu = (returns.mean() * 252).values
    sigma = returns.cov().values
    n_assets = len(mu)

    # Función para minimizar (-Sharpe Ratio)
    def min_var(w, sigma):
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w))) * np.sqrt(252)
        return port_vol
    
    # Restricciones: Suma de pesos = 1
    constraints = ({
        'type': 'eq',
        'fun': lambda w: np.sum(w) - 1
    })

    # Límites: Pesos entre 0 y 1 (no posiciones cortas)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Pesos iniciales (distribuidos uniformemente)
    w0 = np.array([1 / n_assets] * n_assets)

    # Optimización
    result = minimize(min_var, 
            w0, 
            args=(sigma), 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints)
    
    # Resultados
    min_var_weights = result.x

    return min_var_weights


def min_cvar(returns: pd.DataFrame, alpha: float) -> np.array:
    """
    A function to calculate the minimum CVaR portfolio.

    Parameters
    -----------
    returns : pd.DataFrame
        A DataFrame containing the returns of the assets in the portfolio.
    alpha : float
        The alpha value for the CVaR calculation (e.g., 0.05 for 95% confidence).
    
    Returns:
    -----------
    min_cvar_weights : np.array

        An array containing the weights of the minimum CVaR portfolio.
    """

    n_assets = len(returns.columns)

    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    # Better way to calculate CVaR than the one used in my homework 1. I used .query in the homework, but checking with friends this way is better.
    def cvar(portfolio_returns, alpha):
        var = np.percentile(portfolio_returns, alpha*100)
        cvar = -portfolio_returns[portfolio_returns < var].mean()
        return cvar

    def min_cvar(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        return cvar(portfolio_returns, alpha)

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
    ]
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Initial guess
    initial_weights = np.ones(n_assets) / n_assets

    result_min_cvar = minimize(
        fun=min_cvar,
        x0=initial_weights,
        args=(returns, alpha),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        tol=1e-8
    )
    min_cvar_weights = result_min_cvar.x

    return min_cvar_weights


def mcc_portfolio(returns: pd.DataFrame, alpha: float) -> np.array:
    """
    A function to calculate the Minimum CVaR Concentration portfolio.

    Parameters
    -----------
    returns : pd.DataFrame
        A DataFrame containing the returns of the assets in the portfolio.
    alpha : float
        The alpha value for the CVaR calculation (e.g., 0.05 for 95% confidence).

    Returns:
    -----------
    mcc_weights : np.array

        An array containing the weights of the Minimum CVaR Concentration portfolio.
    """

    n_assets = len(returns.columns)

    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    def individual_cvar_contributions(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        var = np.percentile(portfolio_returns, alpha * 100)

        bad_days_portfolio = portfolio_returns < var
        contributions = [-returns.iloc[:, i][bad_days_portfolio].mean() * weights[i] for i in range(n_assets)]
        
        return contributions

    def optimal_mcc(weights, returns, alpha):
        return np.max(individual_cvar_contributions(weights, returns, alpha))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.ones(n_assets) / n_assets

    result = minimize(
        fun=optimal_mcc,
        x0=initial_weights,
        args=(returns, alpha),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        tol=1e-8
    )
    mcc_weights = result.x

    return mcc_weights


def cvar_contributions(weights: list | np.ndarray, returns: pd.DataFrame, alpha: float) -> list:
    """
    A function to calculate the CVaR contributions of each asset in a portfolio.

    Parameters
    -----------
    weights : list | np.ndarray
        A list of weights for the portfolio.
    returns : pd.DataFrame
        A DataFrame containing the returns of the assets in the portfolio.
    alpha : float
        The alpha value for the CVaR calculation (e.g., 0.05 for 95% confidence).

    Returns:
    -----------
    contributions : list

        A list containing the CVaR contributions of each asset in the portfolio.
    """

    n_assets = len(weights)
    # CVaR for only long positions
    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    def individual_cvar_contributions(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        var = np.percentile(portfolio_returns, alpha*100)

        # check which days are in the cvar for the portfolio
        bad_days_portfolio = portfolio_returns < var

        contributions = []
        # chech the returns of each asset the days where the portfolio is in the cvar to know the contribution
        for i in range(n_assets):
            asset_contribution = -returns.iloc[:, i][bad_days_portfolio].mean() * weights[i]
            contributions.append(asset_contribution)
                
        return contributions
    contributions = individual_cvar_contributions(weights, returns, alpha)
    
    return contributions


def plot_weights(stocks: list, weights: list | np.ndarray):
    """
    A function to plot the weights of a portfolio.

    Parameters
    -----------
    stocks : list
        A list of stock tickers.
    weights : list | np.ndarray
        A list of weights for the portfolio

    Returns:
    -----------
        A pie chart showing the portfolio weights.
    """

    df = pd.DataFrame(weights, index=stocks, columns=['w'])
    filtered_df = df[df['w'] > 0.000001]
    labels = filtered_df.index
    values = filtered_df.iloc[: , 0]

    plt.rcParams['figure.facecolor'] = 'lightgray'
    cmap = plt.get_cmap("Blues")
    custom_colors = cmap(np.linspace(0, 1, len(labels)))
    
    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct='%1.2f%%', startangle=90, colors=custom_colors)
    plt.title("Portfolio Weights")
    plt.show()

class BlackScholes:
    def __init__(self):
        """
        A class to implement the Black-Scholes model for option pricing and delta hedging.
        
        Methods:
        --------
        - call_delta(S, k, r, sigma, T): Computes the delta of a European call option.
        - put_delta(S, k, r, sigma, T): Computes the delta of a European put option.
        - delta_hedge(info_call, info_put): Computes the total delta of a portfolio of call and put options.
        """

    def _calculate_d1(self, S, k, r, sigma, T):
        """
        Compute the d1 term used in the Black-Scholes model.
        
        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).
        
        Returns:
        --------
        float

            The d1 value used in the Black-Scholes formula.
        """
        return (np.log(S / k) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    # Deltas
    def call_delta(self, S, k, r, sigma, T):
        """
        Compute the delta of a European call option.
        
        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).
        
        Returns:
        --------
        float

            Delta of the call option.
        """
        return norm.cdf(self._calculate_d1(S, k, r, sigma, T))

    def put_delta(self, S, k, r, sigma, T):
        """
        Compute the delta of a European put option.
        
        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).
        
        Returns:
        --------
        float

            Delta of the put option.
        """
        return np.abs(norm.cdf(self._calculate_d1(S, k, r, sigma, T)) - 1)

    # Hedge
    def delta_hedge(self, info_call, info_put):
        """
        Compute the total delta of a portfolio containing multiple call and put options.
        
        Parameters
        -----------
        info_call : list of lists
            Each inner list contains the parameters [S, K, r, sigma, T, N] for a call option:
            - S: Current stock price
            - K: Strike price
            - r: Risk-free interest rate
            - sigma: Volatility
            - T: Time to maturity
            - N: Number of contracts
        
        info_put : list of lists
            Each inner list contains the parameters [S, K, r, sigma, T, N] for a put option:
            - S: Current stock price
            - K: Strike price
            - r: Risk-free interest rate
            - sigma: Volatility
            - T: Time to maturity
            - N: Number of contracts
        
        Returns:
        --------
        float

            The total delta of the portfolio.
        """

        # Dataframe for call and put options
        df_call = pd.DataFrame(info_call, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])
        df_put = pd.DataFrame(info_put, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])

        df_call['delta'] = df_call.apply(lambda row: BlackScholes().call_delta(*row[0:-1]), axis=1)
        df_put['delta'] = df_put.apply(lambda row: BlackScholes().put_delta(*row[0:-1]), axis=1)
            
        return np.dot(df_call['N'], df_call['delta']) - np.dot(df_put['N'], df_put['delta'])

def var_apl(data: pd.DataFrame, posiciones: list | np.ndarray, conf: float, long: bool):
    """ 
    A function that calculates the Value at Risk (VaR) and Conditional Value at Risk (CVaR) adjusted by liquidity cost for a portfolio.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical exchange rates, indexed by date.
    posiciones : list | np.ndarray
        A list of positions for each currency.
    conf : float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions

    Returns:
    -----------
    resultados : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.
    """

    data = data.sort_index()

    # Bid y Ask
    bid_columns = [col for col in data.columns if 'Bid' in col] # Selecciona las columnas que contienen 'Bid'
    ask_columns = [col for col in data.columns if 'Ask' in col] # Selecciona las columnas que contienen 'Ask'

    # Mid
    mid_columns = [f'Mid.{i}' for i in range(len(bid_columns))] # Se crea una lista con los nombres de las columnas de Mid
    data[mid_columns] = (data[bid_columns].values + data[ask_columns].values) / 2

    # Spreads
    spread_columns = [f'Spread.{i}' for i in range(len(bid_columns))] # Se crea una lista con los nombres de las columnas de Spread
    data[spread_columns] = (data[ask_columns].values - data[bid_columns].values) / data[mid_columns].values

    # Returns
    return_columns = [f'Return.{i}' for i in range(len(mid_columns))] # Se crea una lista con los nombres de las columnas de Return
    data[return_columns] = data[mid_columns].pct_change()

    # Weights
    value = posiciones * data[mid_columns].iloc[-1].values
    pv = np.sum(value)
    w = value / pv

    # Portfolio return
    data['port_ret'] = np.dot(data[return_columns], w)

    # VaR calculation
    var_pct = np.percentile(data['port_ret'].dropna(), 100 - conf*100) if long else np.percentile(data['port_ret'].dropna(), conf*100)
    var_cash = pv * var_pct

    # C-VaR calculation
    cvar_pct = data['port_ret'][data['port_ret'] < var_pct].dropna().mean() if long else data['port_ret'][data['port_ret'] > var_pct].dropna().mean()
    cvar_cash = pv * cvar_pct

    # Liquidity cost
    cl_prom = data[spread_columns].mean()
    cl_estr = np.percentile(data[spread_columns], 99, axis=0)

    # VaR adjusted by liquidity cost

    var_apl_prom, var_apl_estr = np.abs(((var_pct - np.dot(w, cl_prom), var_pct - np.dot(w, cl_estr)) if long 
                                else (var_pct + np.dot(w, cl_prom), var_pct + np.dot(w, cl_estr))))

    var_apl_prom_cash, var_apl_estr_cash = np.abs(((var_cash - np.dot(value, cl_prom), var_cash - np.dot(value, cl_estr)) if long 
                                            else (var_cash + np.dot(value, cl_prom), var_cash + np.dot(value, cl_estr))))
    
    # C-VaR adjusted by liquidity cost

    cvar_apl_prom, cvar_apl_estr = np.abs(((cvar_pct - np.dot(w, cl_prom), cvar_pct - np.dot(w, cl_estr)) if long
                                    else (cvar_pct + np.dot(w, cl_prom), cvar_pct + np.dot(w, cl_estr))))
    
    cvar_apl_prom_cash, cvar_apl_estr_cash = np.abs(((cvar_cash - np.dot(value, cl_prom), cvar_cash - np.dot(value, cl_estr)) if long
                                            else (cvar_cash + np.dot(value, cl_prom), cvar_cash + np.dot(value, cl_estr))))

    resultados = pd.DataFrame({
        'Métrica': ['VaR', 'VaR Ajustado Promedio', 'VaR Ajustado Estresado', 'C-VaR', 'C-VaR Ajustado Promedio', 'C-VaR Ajustado Estresado'],
        'Porcentaje': [np.abs(var_pct), var_apl_prom, var_apl_estr, np.abs(cvar_pct), cvar_apl_prom, cvar_apl_estr],
        'Cash': [np.abs(var_cash), var_apl_prom_cash, var_apl_estr_cash, np.abs(cvar_cash), cvar_apl_prom_cash, cvar_apl_estr_cash]
    })

    return resultados
@dataclass
class Position:
    """ 
    A cool representation of a position
    """
    ticker: str
    n_shares: int
    price: float
    sl: float
    tp: float
    margin_account: float
    margin_requirement: float

def get_portfolio_value(cash: float, long_ops: list[Position], short_ops: list[Position], current_price: float, n_shares: int, COM: float) -> float:
    val = cash

    # Add long positions value
    val += len(long_ops) * current_price * n_shares

    # Add short positions equity (margin_account + margin_requirement - cost to cover)
    for pos in short_ops:
        cover_cost = current_price * pos.n_shares * (1 + COM)  # include commission
        val += pos.margin_account + pos.margin_requirement - cover_cost

    return val

def backtest_one_indicator(data: pd.DataFrame, COM: float, BORROW_RATE: float, INITIAL_MARGIN: float, MAINTENANCE_MARGIN: float, 
                           STOP_LOSS: float, TAKE_PROFIT: float, N_SHARES: int, initial_capital: float, time_frame: float) -> tuple[float, list[float]]:
    """
    A function to backtest a trading strategy based on buy and sell signals.

    **Important**: Dataframe must have a column called 'buy_signal' and another called 'sell_signal' 
    with boolean values as well as the column with the 'Close' prices.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices and buy/sell signals, indexed by date.
    COM : float
        Commission rate per trade (e.g., 0.001 for 0.1% commission).
    BORROW_RATE : float
        Annual borrow rate for short selling (e.g., 0.05 for 5% annual rate).
    INITIAL_MARGIN : float
        Initial margin requirement for short selling (e.g., 0.5 for 50% margin).
    MAINTENANCE_MARGIN : float
        Maintenance margin requirement for short selling (e.g., 0.3 for 30% margin).
    STOP_LOSS : float
        Stop loss percentage (e.g., 0.02 for 2% stop loss).
    TAKE_PROFIT : float
        Take profit percentage (e.g., 0.04 for 4% take profit).
    N_SHARES : int
        Number of shares to trade per signal.
    initial_capital : float
        Initial capital for the backtest.
    time_frame : float
        Time frame of the data in minutes (e.g., 5 for 5-minute bars)

    Returns:
    -----------
    capital : float

        The final capital after the backtest.
    portfolio_value : list[float]

        A list containing the portfolio value at each time step.
    """
    
    capital = initial_capital
    portfolio_value = [capital]
    active_long_positions: list[Position] = []
    active_short_positions: list[Position] = []
    
    bars_per_year = 252 * 6.5 * 60 / time_frame  # 252 trading days, 6.5 hours per day, 5-min bars
    bar_borrow_rate = (1 + BORROW_RATE) ** (1 / bars_per_year) - 1

    for i, row in data.iterrows():
        # -- LONG -- #
        # Check active orders
        for position in active_long_positions.copy():
            # Stop loss or take profit check
            if row.Close > position.tp or row.Close < position.sl:
                # Add profits / losses to capital
                capital += row.Close * position.n_shares * (1 - COM)
                # Remove position from active position
                active_long_positions.remove(position)

        # -- SHORT -- #
        for position in active_short_positions.copy():
            # Apply borrow rate to active short positions
            cover_cost = row.Close * position.n_shares * (1 + COM)
            position.margin_account -= row.Close * position.n_shares * bar_borrow_rate

            margin_deposit = position.margin_requirement
            equity = (position.margin_account + margin_deposit) - cover_cost

            # Required Equity
            required_equity = MAINTENANCE_MARGIN * cover_cost

            # Check Margin call
            if equity < required_equity:
                # Margin Call
                deposit = required_equity - equity

                if capital > deposit:
                    capital -= deposit
                else:
                    # We have to close the position
                    capital += position.margin_account + position.margin_requirement - cover_cost
                    active_short_positions.remove(position)
                    continue

            else:
                # Stop loss or take profit check
                if row.Close < position.tp or row.Close > position.sl:
                    # Add profits / losses to capital
                    capital += position.margin_account + position.margin_requirement - cover_cost
                    # Remove position from active position
                    active_short_positions.remove(position)

        # Check Long Signal
        if getattr(row, 'buy_signal', False):
            cost = row.Close * N_SHARES * (1 + COM)

            # Do we have enough cash?
            if capital > cost:
                # Discount cash
                capital -= cost
                # Add position to portfolio
                pos = Position(ticker='AAPL', n_shares=N_SHARES, price=row.Close,
                            sl=row.Close * (1 - STOP_LOSS), tp=row.Close*(1 + TAKE_PROFIT),
                            margin_account=0, margin_requirement=0)
                active_long_positions.append(pos)

        # Check Short Signal
        if getattr(row, 'sell_signal', False):
            short_value = row.Close * N_SHARES
            margin_requirement = short_value * INITIAL_MARGIN
            
            # Do we have enough cash?
            if capital > margin_requirement:
                # Setting up the margin account
                margin_account = row.Close * N_SHARES * (1 - COM)
                # Discount cash
                capital -= margin_requirement

                pos = Position(ticker='AAPL', n_shares=N_SHARES, price=row.Close,
                            sl=row.Close * (1 + STOP_LOSS), tp=row.Close*(1 - TAKE_PROFIT),
                            margin_account=margin_account, margin_requirement=margin_requirement)
                active_short_positions.append(pos)

        # Calculate portfolio value
        portfolio_value.append(get_portfolio_value(capital, active_long_positions, active_short_positions, row.Close, N_SHARES, COM))

    # At the end of the backtesting, we should close all active positions
    capital += row.Close * len(active_long_positions) * N_SHARES * (1 - COM)

    for position in active_short_positions:
        capital += position.margin_account + position.margin_requirement - (row.Close * position.n_shares * (1 + COM))

    active_long_positions = []
    active_short_positions = []

    return capital, portfolio_value
