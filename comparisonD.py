import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import plotly as px
from prophet.plot import add_changepoints_to_plot
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from prophet.plot import plot_cross_validation_metric
from plotly import graph_objs as go



st.title("Finance Dachboard")
tickers = ('AAPL','AMD','AMZN','TSLA','MSFT','GOOGL','WMT','V','NFLX','PYPL')
dropdown = st.multiselect('Pick your stock',tickers)


n_years = st.slider('Years of prediction:', 1, 4)
period = n_years* 365

start=st.date_input('Start', value=pd.to_datetime('2015-01-01'))
end=st.date_input('End', value=pd.to_datetime('today'))
CDF=pd.DataFrame(columns=["StockName","TodayPrice","PredectionPrice","ChangeRatio"])

@st.cache
def load_data(ticker):
    data = yf.download(ticker, start, end)
    data.reset_index(inplace=True)
    return data



def relativeret(df):
    rel=df.pct_change()
    cumret=(1+rel).cumprod()-1
    cumret= cumret.fillna(0)
    return cumret

if len(dropdown)>0:
    df=relativeret(yf.download(dropdown,start,end)['Adj Close'])
    st.header('Annual Returns of {}'.format(dropdown))
    st.line_chart(df)



for i in dropdown:
    Data=load_data(i)
    
    df_train = Data[['Date','Close']]
    df_train = df_train.rename(columns={'Date': "ds", "Close": "y"})
    df_train['ds'] = df_train['ds'].dt.tz_convert(None)

    m = Prophet(interval_width=0.95)
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period,freq = 'D')
    forecast = m.predict(future)

    st.subheader('3.Forecast data : '+i)
    A=forecast['trend'].tail(1).mean()
    B=Data['Close'].tail(1).mean()
    result1=(A-B)/B*100
    CDF=CDF.append(pd.DataFrame({"StockName":[i],"TodayPrice":[B],"PredectionPrice":[A],"ChangeRatio":[result1]}))
    
    st.write(f'Forecast plot for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)
st.write('4.The result of prediction is : ')
st.write(CDF)

FCDF=CDF.sort_values(['ChangeRatio'])
st.write('5.The stock you should invest is: ')
st.write(FCDF.tail(1))

