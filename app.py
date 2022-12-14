import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
from datetime import date, timedelta
import plotly.graph_objects as go

from tensorflow.keras.models import load_model
loaded_model = load_model('lstm.h5')

# model = pickle.load(open('model_pkl','rb'))
today = date.today()
d1 = today.strftime("%Y-%m-%d")
end_date = d1
d2 = date.today() - timedelta(days=1825)  # 5 years data
d2 = d2.strftime("%Y-%m-%d")
start_date = d2
st.title("Crpytocurrencies Prediction")
st.subheader("What is Cryptocurrency???")
st.write("""
You must have heard or invested in any cryptocurrency once in your life. 
It is a digital medium of exchange that is encrypted and decentralized. 
Many people use cryptocurrencies as a form of investing because it gives great returns even in a short period. 
Bitcoin, Ethereum, Dogecoin & many more coins are among the popular cryptocurrencies today.
""")
selected_stock= st.sidebar.selectbox("Select the crpytocurrency for prediction",
                                     ("BTC-USD","ETH-USD","XRP-USD","DOGE-USD","ADA-USD",
                                      "BNB-USD","DOT-USD","SHIB-USD","TRX-USD","MATIC-USD"))
st.write("### Selected cryptocurrency : ", selected_stock )

def data_load(ticker):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("loading data.....")
data = data_load(selected_stock)
data_load_state.text("loading data... done")

#data
st.subheader("Raw Data")
st.write(data.tail())

#Describing data
st.subheader("Data is from 2017 to 2022")
st.write(data.describe())

#visualization
def plot_data():
    figure = go.Figure(data=[go.Candlestick(x=data["Date"],
                                            open=data["Open"],
                                            high=data["High"],
                                            low=data["Low"],
                                            close=data["Close"])])
    figure.update_layout(title_text = "Interactive Price Chart",xaxis_rangeslider_visible=True)
    st.plotly_chart(figure)

plot_data()

df = data['Close'] # forecast close
from sklearn.preprocessing import MinMaxScaler
import numpy as np
scaler = MinMaxScaler(feature_range = (0,1))
data1 = scaler.fit_transform(np.array(df).reshape(-1,1))

# train test split
train_size = int(len(data1)*0.75)
test_size = len(data1) - train_size
train_data, test_data = data1[0:train_size,:],data1[train_size:len(data1),:1]

def create_data(dataset,time_step = 1):
    dataX, dataY = [],[]
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)

# past 100 days
time_step = 100
x_train, y_train = create_data(train_data,time_step)
x_test,y_test = create_data(test_data,time_step)
x_train = x_train.reshape(x_train.shape[0],x_train.shape[1],1)
x_test = x_test.reshape(x_test.shape[0],x_test.shape[1],1)

train_predict = loaded_model.predict(x_train)
test_predict = loaded_model.predict(x_test)
##Transform back to original form
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)

# Final Graph
# Plotting
look_back = 100
# shift train prediction for plotting
trainPredict = np.empty_like(data1)
trainPredict[:,:] = np.nan
trainPredict[look_back:len(train_predict)+look_back, :] = train_predict

# shift test prediction
testPredict = np.empty_like(data1)
testPredict[:,:] = np.nan
testPredict[len(train_predict) + (look_back * 2)+1:len(data1)-1, :] = test_predict

# plot baseline and predictions
fig2 = plt.figure(figsize = (12,6))
plt.plot(scaler.inverse_transform(data1))
plt.plot(trainPredict)
plt.plot(testPredict)
plt.legend()
st.pyplot(fig2)

st.write("Green indicates the Predicted Data")
st.write("Blue indicates the Complete Data")
st.write("Orange indicates the Train Data")

