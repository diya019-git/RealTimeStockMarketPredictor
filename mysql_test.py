import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="chiragsql@2002",
    database="stock_project"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50),
    timestamp DATETIME,
    price FLOAT,
    ma5 FLOAT,
    rsi FLOAT
)
""")

print("Table created / already exists")