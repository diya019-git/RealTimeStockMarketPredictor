import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_price(symbol):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chiragsql@2002",
        database="stock_project"
    )

    query = """
    SELECT price FROM stock_data
    WHERE symbol=%s
    ORDER BY id ASC
    """

    df = pd.read_sql(query, conn, params=(symbol,))

    conn.close()

    if len(df) < 10:
        return None

    df['time_index'] = range(len(df))

    X = df[['time_index']]
    y = df['price']

    model = LinearRegression()
    model.fit(X, y)

    next_index = [[len(df)]]

    prediction = model.predict(next_index)

    return float(prediction[0])