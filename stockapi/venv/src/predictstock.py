import os
import pandas as pd

import numpy as np
import yfinance as yf
from datetime import datetime
import datetime as dt
import math
import random
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def predictStock(quote, l):
    end = datetime.now()
    start = datetime(end.year-5, end.month, end.day)
    data = yf.download(quote, start=start, end=end)
    df = pd.DataFrame(data=data)
    df.to_csv(''+quote+'.csv')
    df = pd.read_csv(''+quote+'.csv')
    df.dropna()

    # data preprocessing
    code_list = []
    for i in range(0, len(df)):
        code_list.append(quote)
    df2 = pd.DataFrame(code_list, columns=['Code'])
    df2 = pd.concat([df2, df], axis=1)
    df = df2
    dataset_train = df.iloc[0:int(0.8*len(df)), :]
    dataset_test = df.iloc[int(0.8*len(df)):, :]
    training_set = df.iloc[:, 4:5].values

    # normalizing the data
    from sklearn.preprocessing import MinMaxScaler
    sc = MinMaxScaler(feature_range=(0, 1))  # Scaled values btween 0,1
    training_set_scaled = sc.fit_transform(training_set)

    X_train = []  # memory with 30 days from day i
    y_train = []  # day i
    for i in range(30, len(training_set_scaled)):
        X_train.append(training_set_scaled[i-30:i, 0])
        y_train.append(training_set_scaled[i, 0])
        # Convert list to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_forecast = np.array(X_train[-1, 1:])
    X_forecast = np.append(X_forecast, y_train[-1])
    # Reshaping: Adding 3rd dimension
    # .shape 0=row,1=col
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_forecast = np.reshape(X_forecast, (1, X_forecast.shape[0], 1))

    from keras.models import Sequential
    from keras.layers import Dense
    from keras.layers import Dropout
    from keras.layers import LSTM

    # building the model
    regressor = Sequential()

    # Add first LSTM layer
    regressor.add(LSTM(units=50, activation="relu", return_sequences=True,
                       input_shape=(X_train.shape[1], 1)))
    # units=no. of neurons in layer
    # input_shape=(timesteps,no. of cols/features)
    # return_seq=True for sending recc memory. For last layer, retrun_seq=False since end of the line
    regressor.add(Dropout(0.1))

    # Add 2nd LSTM layer
    regressor.add(LSTM(units=50, activation="relu", return_sequences=True))
    regressor.add(Dropout(0.1))

    # Add 3rd LSTM layer
    regressor.add(LSTM(units=50, activation="relu", return_sequences=True))
    regressor.add(Dropout(0.1))

    # Add 4th LSTM layer
    regressor.add(LSTM(units=50, activation="relu", return_sequences=False))
    regressor.add(Dropout(0.1))

    # Add o/p layer
    regressor.add(Dense(units=1))

    # Compile
    regressor.compile(optimizer='adam', loss='mean_squared_error')

    # Training
    regressor.fit(X_train, y_train, epochs=40, batch_size=30)
    # For lstm, batch_size=power of 2

# Testing

    # dataset_test=pd.read_csv('Google_Stock_Price_Test.csv')
    real_stock_price = dataset_test.iloc[:, 4:5].values

# To predict, we need stock prices of 7 days before the test set
    # So combine train and test set to get the entire data set
    dataset_total = pd.concat(
        (dataset_train['Close'], dataset_test['Close']), axis=0)
    testing_set = dataset_total[len(
        dataset_total) - len(dataset_test) - 30:].values
    testing_set = testing_set.reshape(-1, 1)
    # -1=till last row, (-1,1)=>(80,1). otherwise only (80,0)

    # Feature scaling
    testing_set = sc.transform(testing_set)

    # Create data structure
    X_test = []
    for i in range(30, len(testing_set)):
        X_test.append(testing_set[i-30:i, 0])
        # Convert list to numpy arrays
    X_test = np.array(X_test)

    # Reshaping: Adding 3rd dimension
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # Testing Prediction
    predicted_stock_price = regressor.predict(X_test)

    # Getting original prices back from scaled values
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    fig = plt.figure(figsize=(7.2, 4.8), dpi=65)
    plt.plot(real_stock_price, label='Actual Price')
    plt.plot(predicted_stock_price, label='Predicted Price')

    plt.legend(loc=4)
    # plt.savefig(os.path.join(os.path.abspath(__file__)))

    plt.savefig(os.path.join(os.getcwd(), 'public/{}.png'.format(quote)))
    plt.close(fig)

    error_lstm = math.sqrt(mean_squared_error(
        real_stock_price, predicted_stock_price))

    # Forecasting Prediction
    forecasted_stock_price = regressor.predict(X_forecast)

    # Getting original prices back from scaled values
    forecasted_stock_price = sc.inverse_transform(forecasted_stock_price)

    lstm_pred = forecasted_stock_price[0, 0]
    # print()
    # print("##############################################################################")
    # print("Tomorrow's ", 'amzn', " Closing Price Prediction by LSTM: ", lstm_pred)
    # print("LSTM RMSE:", error_lstm)
    # print("##############################################################################")
    # print()
    l['lstm_pred'] = lstm_pred
    l['error_lstm'] = error_lstm
    return l
