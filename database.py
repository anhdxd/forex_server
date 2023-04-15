import sqlite3
from globals_var import lst_symbol_as, database_name

class MyDatabase:
    def __init__(self):
        pass

    def create_database():
        # Create database
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        # Create table - diary, chinese - text, time - integer if not exist
        c.execute('''CREATE TABLE IF NOT EXISTS tb_notify (symbol TEXT, price REAL)''')
        #c.execute('''CREATE TABLE diary (text TEXT, time INTEGER)''')
        conn.close()

    def insert_notify(symbol, price):
        #price có thể là list => tách ra thành nhiều dòng. là string => add vào 1 dòng
        try:
            if symbol in lst_symbol_as:
                conn = sqlite3.connect(database_name)
                c = conn.cursor()
                # Insert a row of data
                if type(price) is list:
                    for p in price:
                        c.execute("INSERT INTO tb_notify VALUES (?, ?)", (symbol, p))
                else:
                    c.execute("INSERT INTO tb_notify VALUES (?, ?)", (symbol, price))
                # Save the changes
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print("Exception insert db:" + e)
            return False
        return False

    def get_notify():
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        #select where symbol='gu' and price = 123
        c.execute("SELECT * FROM tb_notify")
        #c.execute("SELECT * FROM tb_notify WHERE symbol = ? AND ", (symbol,))
        
        data = c.fetchall()
        #print(data)
        conn.close()
        return data
    
    #delete in db
    def delete_notify(symbol, price):
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        #select where symbol='gu' and price = 123
        #check if price is list
        if type(price) is list:
            for p in price:
                c.execute("DELETE FROM tb_notify WHERE symbol = ? AND price = ?", (symbol, p))
        else:
            c.execute("DELETE FROM tb_notify WHERE symbol = ? AND price = ?", (symbol, price))
        #c.execute("SELECT * FROM tb_notify WHERE symbol = ? AND ", (symbol,))
        
        conn.commit()
        conn.close()
    
# sqDB = MyDatabase
# sqDB.create_database()
# sqDB.insert_notify("gu", [1.24146,1.2415,1.2416,1.2418,1.2419])
# sqDB.insert_notify("xu", [2004.270,2004,2005.270,2005,2006])
# sqDB.get_notify("gu")
# lst_notify = sqDB.get_notify()
# print(lst_notify)
# # to dataframe
# import pandas as pd
# from globals_var import lst_symb_map, dic_syb_db_map
# # to dataframe column 'gu' and 'eu'
# prices = {'OANDA:GBP_USD': 1.24898, 'OANDA:XAU_USD': 2004.275, 'OANDA:GBP_JPY': 166.058, 'OANDA:AUD_USD': 0.671025, 'OANDA:USD_CAD': 1.3359450000000002, 'OANDA:AUD_JPY': 89.7535}
# df_notify = pd.DataFrame(lst_notify, columns=['symbol', 'price']).drop_duplicates()
# df_notify['symbol'] = df_notify['symbol'].map(lst_symb_map)
# print(df_notify)
# #check if prices have symbol and price in df_notify
# for key, value in prices.items():
#     if key in df_notify['symbol'].values:
#         # Nếu giá trị lệch 0.01% với giá trị trong db thì xóa
#         cond = abs(df_notify[df_notify['symbol'] == key]['price'].values - value) <= (value*0.01/100)
#         #print(cond)
#         if cond.any():
#             print("found")
#             print(df_notify[df_notify['symbol'] == key]['price'].values[cond].tolist())
#             sqDB.delete_notify(dic_syb_db_map[key], df_notify[df_notify['symbol'] == key]['price'].values[cond].tolist())
#             print("deleted")
#     else:
#         print("not found")

# lst_notify = sqDB.get_notify()
# print(lst_notify)