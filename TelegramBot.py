#!/usr/bin/env python3
import pytz
from datetime import datetime
import time
import queue
import globals_var as gv
from telegram.ext import Updater, JobQueue, MessageHandler, Filters
import re
from database import MyDatabase as sqDB
import threading
from globals_var import event_breaktime,dict_price_rt

event_reloadDB = threading.Event()

# #open file and write log
def write_log(text, filename='my_log.txt'):
    #get time format
    now = datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))
    #now = now + datetime.timedelta(hours=7)
    time = now.strftime("%H:%M:%S")
    text = time + ' - ' + text
    with open('log/log.txt', 'a', encoding='utf-8') as f:
        f.write(text + '\n')
def check_size_log_folder():
  import os
  import glob
  #import shutil
  # Get current size of log folder
  path = 'log/'
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(path):
      for f in filenames:
          fp = os.path.join(dirpath, f)
          total_size += os.path.getsize(fp)
  # If size > 50MB then remove all log files
  if total_size > 50000000:
    files = glob.glob('log/*')
    for f in files:
      os.remove(f)

# Telegram bot
def gu_command_handler(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Nhập giá thông báo GBPUSD")
    while True:
      # Check for new updates
      try:
          update = context.dispatcher.update_queue.get_nowait()
      except queue.Empty:
          time.sleep(0.5)
          continue
      
      if update.message and update.message.text.startswith('/'):
          update.message.reply_text('GU command has ended.')
          return
      
      # Get the message text
      text = update.message.text
      context.bot.send_message(chat_id=update.effective_chat.id, text=f"GU: {text}")

def allmessage_handler(update, context):
    text = str(update.message.text)
    lst_symbol = gv.lst_symbol_as
    try:
      if text.lower()[:2] in lst_symbol:
        regex = r'^'+ text.lower()[:2] + r'\s[\d.\s]+$'
        # Regex match sau symbol name
        if re.match(regex, text.lower()):
          numbers =  [float(num) for num in re.findall(r'[\d.]+', text.lower())]
          sqDB.insert_notify(text.lower()[:2], numbers)
          context.bot.send_message(chat_id=update.effective_chat.id, text=f"Đã lưu thông báo: {numbers}")
          event_reloadDB.set()
        else:
          context.bot.send_message(chat_id=update.effective_chat.id, text=f"Gửi sai định dạng: {text}")
        return
    except Exception as e:
      context.bot.send_message(chat_id=update.effective_chat.id, text=f"Exception: {e}")
      return
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Đã gửi: {text}")
    
def thread_sendnotify(bot):
  from pandas import DataFrame
  try:

    global dict_price_rt
    
    #in_bot = Updater.bot(bot)
    #from globals_var import dict_price_rt, lst_symb_map, dic_syb_db_map
    # Lấy các thông báo từ db
    lst_notify = sqDB.get_notify()
    df_notify = DataFrame(lst_notify, columns=['symbol', 'price']).drop_duplicates()
    df_notify['symbol'] = df_notify['symbol'].map(gv.lst_symb_map)

    while 1:
      # event được set có nghĩa là thứ 7 chủ nhật
      if event_breaktime.is_set():
        #print("stop")
        time.sleep(gv.break_time)
        continue
      #print(df_notify)
      time.sleep(0.5)
      reload_db = False
      #print(gv.dict_price_rt)
      #check if prices have symbol and price in df_notify
      for key, value in dict_price_rt.items():
          if key in df_notify['symbol'].values:
              # Nếu giá trị lệch 0.01% với giá trị trong db thì xóa
              #print(f"price:{df_notify[df_notify['symbol'] == key]['price'].values}" )
              cond = abs(df_notify[df_notify['symbol'] == key]['price'].values - value) <= (value*0.02/100)
              #print(cond)
              if cond.any():
                  #print("found")
                  #print(df_notify[df_notify['symbol'] == key]['price'].values[cond].tolist())
                  bot.send_message(chat_id=gv.chatid, text=f"{key} - {value}")
                  sqDB.delete_notify(gv.dic_syb_db_map[key], df_notify[df_notify['symbol'] == key]['price'].values[cond].tolist())
                  reload_db = True
                  #print("deleted")
                      # reload DB
      # reload database                  
      if reload_db or event_reloadDB.is_set():
        lst_notify = sqDB.get_notify()
        df_notify = DataFrame(lst_notify, columns=['symbol', 'price']).drop_duplicates()
        df_notify['symbol'] = df_notify['symbol'].map(gv.lst_symb_map)
        event_reloadDB.clear()
  except Exception as e:
    #print(e)
    bot.send_message(chat_id=gv.chatid, text=f"Exception sendnotify: {e}")

def thread_checktime():
  global event_breaktime
  global event_reloadDB
  while 1:
    #print(datetime.datetime.now().weekday())
    now = datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))
    print(now.weekday())
    if now.weekday() == 5 or now.weekday() == 6:
      event_breaktime.set()
      #dict_price_rt = {key: 0 for key in gv.lst_symbol_oanda}
    else:
        event_breaktime.clear()
        #event_reloadDB.is_set()

    time.sleep(gv.break_time)
    
def main():
  #thread check time break
  thread_time = threading.Thread(target=thread_checktime)
  thread_time.daemon = True
  thread_time.start()

  token = gv.telebot_token
  updater = Updater(token=token, use_context=True)

  dispatcher = updater.dispatcher

  # Đăng ký các command handler
  # start_handler = CommandHandler('gu', gu_command_handler)
  # dispatcher.add_handler(start_handler)

  message_handler = MessageHandler(Filters.text, allmessage_handler)
  dispatcher.add_handler(message_handler)
  # get list command
  updater.start_polling()

    # Thread price
  import forexprice
  thread_fx = threading.Thread(target=forexprice.main_socket)
  thread_fx.daemon = True
  thread_fx.start()

  #thread send notify
  thread = threading.Thread(target=thread_sendnotify, args=(updater.bot,))
  thread.daemon = True
  thread.start()

  updater.idle()

# Main
if __name__ == "__main__":
  sqDB.create_database()
  main()

  # import threading
  # #create thread forex price
  # thread_forex = threading.Thread(target=forexprice.main_socket)
