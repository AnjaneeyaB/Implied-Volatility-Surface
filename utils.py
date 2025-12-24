import QuantLib as ql
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.interpolate import griddata

def impliedVolFromMarketPrice(market_price, underlying_spot=100.0, risk_free_rate=0.05, time_to_expiry=1.0, strike_price=100.0, option_type='call', initial_vol_guess=0.20, dividend_yield = 0.03):

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    expiry_date = today + int(time_to_expiry * 365)

    payoff = ql.PlainVanillaPayoff(ql.Option.Call if option_type.lower() == 'call' else ql.Option.Put, strike_price)
    option = ql.EuropeanOption(payoff, ql.EuropeanExercise(expiry_date))

    spot = ql.SimpleQuote(underlying_spot)
    rate = ql.SimpleQuote(risk_free_rate)
    div = ql.SimpleQuote(dividend_yield)
    vol = ql.SimpleQuote(initial_vol_guess)

    riskFreeCurve = ql.FlatForward(0, ql.NullCalendar(), ql.QuoteHandle(rate), ql.Actual365Fixed(),ql.Continuous)
    dividendCurve = ql.FlatForward(0, ql.NullCalendar(), ql.QuoteHandle(div),ql.Actual365Fixed(), ql.Continuous)
    volCurve = ql.BlackConstantVol(0, ql.NullCalendar(), ql.QuoteHandle(vol), ql.Actual365Fixed())
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(spot), ql.YieldTermStructureHandle(dividendCurve), ql.YieldTermStructureHandle(riskFreeCurve), ql.BlackVolTermStructureHandle(volCurve))
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    implied_vol = option.impliedVolatility(market_price,process)

    return implied_vol

def impliedVolatilitySurface(start_date = pd.Timestamp('2022-10-01'), end_date = pd.Timestamp('2022-12-31'), risk_free_rate = 0.05, dividend_yield = 0.03):
    x = list()
    y = list()
    z = list()
    data1 = pd.read_csv('data/Aapl_2016_2020.csv')
    data2 = pd.read_csv('data/aapl_2021_2023.csv')
    data = pd.concat([data1, data2])
    data.columns
    # print(data.isna().sum())

    cols = [' [QUOTE_DATE]', ' [UNDERLYING_LAST]', ' [EXPIRE_DATE]', ' [C_LAST]', ' [C_BID]', ' [C_ASK]', ' [STRIKE]']
    data = data[cols]
    data[' [QUOTE_DATE]'] = pd.to_datetime(data[' [QUOTE_DATE]'])
    data[' [EXPIRE_DATE]'] = pd.to_datetime(data[' [EXPIRE_DATE]'])
    data[' [C_ASK]'] = pd.to_numeric(data[' [C_ASK]'], errors='coerce')
    data[' [C_BID]'] = pd.to_numeric(data[' [C_BID]'], errors='coerce')
    data[' [C_MARK]'] = (data[' [C_ASK]'] + data[' [C_BID]'])/2
    data[' [T]'] = ((data[' [EXPIRE_DATE]'] - data[' [QUOTE_DATE]']).dt.days.clip(lower=1) / 365.0) # type: ignore

    cols = [' [QUOTE_DATE]', ' [UNDERLYING_LAST]', ' [EXPIRE_DATE]', ' [STRIKE]', ' [C_MARK]', ' [T]']
    data = data[cols]

    data = data[(data[' [EXPIRE_DATE]'] >= start_date) & (data[' [EXPIRE_DATE]'] <= end_date)]

    for i in range(len(data)):
        # print(i)
        try:
            iv = impliedVolFromMarketPrice(market_price=data[' [C_MARK]'].iloc[i], underlying_spot=data[' [UNDERLYING_LAST]'].iloc[i], time_to_expiry=data[' [T]'].iloc[i], strike_price=data[' [STRIKE]'].iloc[i], risk_free_rate=risk_free_rate, dividend_yield=dividend_yield)
            moneyness = np.log(data[' [UNDERLYING_LAST]'].iloc[i]/data[' [STRIKE]'].iloc[i])
            if moneyness < 0:
                pass
            else:
                x.append(data[' [T]'].iloc[i])
                y.append(moneyness)
                z.append(iv)
        except RuntimeError:
            pass
    grid_size = 100  

    xi = np.linspace(min(x), max(x), grid_size)
    yi = np.linspace(min(y), max(y), grid_size)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata(
        points=(x, y),
        values=z,
        xi=(xi, yi),
        method="linear"  
    )

    fig = go.Figure(
        data=go.Surface(
            x=xi,
            y=yi,
            z=zi,
            colorscale="Viridis",
            colorbar=dict(title="Implied Volatility")
        )
    )

    fig.update_layout(
        title="Implied Volatility Surface",
        width=1000,
        height=800,
        scene=dict(
            xaxis_title="Time to Expiry",
            yaxis_title="Moneyness",
            zaxis_title="Implied Volatility(%)"
        )
    )

    return fig


if __name__ == '__main__':
    # iv = impliedVolFromMarketPrice(10.45)
    # print(iv)
    fig = impliedVolatilitySurface()
    print(fig.show())