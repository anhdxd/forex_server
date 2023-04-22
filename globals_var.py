import threading
telebot_token = '5897751187:AAF6EQJlUJEIgpCwwV3v0qs6KY2pOV5yOuw'
lst_symbol_as = ['gu', 'xu', 'uc', 'au', 'gj', 'aj'] # List symbol allow send notify
finnhub_token = "cgshbk1r01qkrsgj8v00cgshbk1r01qkrsgj8v0g"
database_name = 'notify.db'
lst_symbol_oanda = ['OANDA:GBP_USD', 'OANDA:XAU_USD', 'OANDA:GBP_JPY', 'OANDA:AUD_USD','OANDA:USD_CAD','OANDA:AUD_JPY']
dic_syb_db_map = {'OANDA:GBP_USD': 'gu', 'OANDA:XAU_USD': 'xu', 'OANDA:GBP_JPY': 'gj', 'OANDA:AUD_USD': 'au', 'OANDA:USD_CAD': 'uc', 'OANDA:AUD_JPY': 'aj'}
lst_symb_map = {'gu': 'OANDA:GBP_USD', 'xu': 'OANDA:XAU_USD', 'uc': 'OANDA:USD_CAD', 'au': 'OANDA:AUD_USD', 'gj': 'OANDA:GBP_JPY', 'aj': 'OANDA:AUD_JPY'}
dict_price_rt = {key: 0 for key in lst_symbol_oanda} # real time candle globals
chatid = 1042979764
event_breaktime = threading.Event()
break_time = 6*3600