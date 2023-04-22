
# import finnhub
# finnhub_client = finnhub.Client(api_key="cgshbk1r01qkrsgj8v00cgshbk1r01qkrsgj8v0g")

# print(finnhub_client.forex_symbols('OANDA'))
import websocket
import json
from globals_var import lst_symbol_oanda, finnhub_token, dict_price_rt, event_breaktime, break_time
from datetime import datetime
from pytz import timezone

def exchange_price(json_data):
    global dict_price_rt

    # loop through the json_data['data'] list
    for i in range(len(json_data['data'])):
        symbol = json_data['data'][i]['s']
        if symbol in dict_price_rt.keys():
            dict_price_rt[symbol] = json_data['data'][i]['p']
#https://pypi.org/project/websocket_client/

def on_message(ws, message):
    if event_breaktime.is_set():
        print("close socket")
        ws.close()

    jdata = json.loads(message)
    #check if jdata['data'] exists
    if 'data' in jdata.keys():
        exchange_price(jdata)
        #print(dict_price_rt)
    # print(str(jdata['data'][0]['s']) + " " + str(jdata['data'][0]['p']))



def on_error(ws, error):
    print("error"+ str(error))

def on_close(ws, close_status_code, close_msg):
    print(">>>>>>CLOSED")

def on_open(ws):
    print("open websocket")
    for symbol in lst_symbol_oanda:
        ws.send('{"type":"subscribe","symbol":"'+ symbol +'"}')

def main_socket():
    global event_breaktime
    global dict_price_rt
    try:
        import time
        while 1:
            if event_breaktime.is_set():
                print("stop")
                for symbol in dict_price_rt.keys():
                    dict_price_rt[symbol] = 0
                time.sleep(break_time)#(6*3600)
                continue

            ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={finnhub_token}",
                                      on_message = on_message,
                                      on_error = on_error,
                                      on_close = on_close)
            ws.on_open = on_open
            ws.run_forever()

    except Exception as e:
        print("Exception: ", e)

if __name__ == "__main__":
    #websocket.enableTrace(True)
    #main_socket()
    pass

        