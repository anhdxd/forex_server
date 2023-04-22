#!/usr/bin/env python3
import pytz
import requests
import datetime
import re
import time
import sqlite3
import telegram
import docx
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from io import BytesIO
import os 
import threading
import random


docx_name = 'expForex.docx'
wait_time = 7200
event_changeword = threading.Event()

# Class DB img
class DBImg:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS img (id_img INTEGER PRIMARY KEY,classify TEXT, img1 BLOB, img2 BLOB )''')
        self.conn.commit()
        self.c.close()

    def insert(self, img, date):
        self.c = self.conn.cursor()
        self.c.execute("INSERT INTO img (id_img, classify, img1, img2) VALUES (?, ?)", (img, date))
        self.conn.commit()
        self.c.close()

    def get_all(self):
        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM img")
        data = self.c.fetchall()
        self.c.close()
        return data

    def get_all_by_date(self, date):
        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM img WHERE date = ?", (date,))
        data = self.c.fetchall()
        self.c.close()
        return data

    def get_all_by_id(self, id):
        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM img WHERE id = ?", (id,))
        data = self.c.fetchall()
        self.c.close()
        return data

    def delete(self, id):
        self.c = self.conn.cursor()
        self.c.execute("DELETE FROM img WHERE id = ?", (id,))
        self.conn.commit()
        self.c.close()

    def delete_all(self):
        self.c = self.conn.cursor()
        self.c.execute("DELETE FROM img")
        self.conn.commit()
        self.c.close()

    def close(self):
        self.conn.close()
#open file and write log
def write_log(text, filename='log_forex.txt'):
    #get time format
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))
    #now = now + datetime.timedelta(hours=7)
    time = now.strftime("%H:%M:%S")
    text = time + ' - ' + text
    with open('log/log.txt', 'a', encoding='utf-8') as f:
        f.write(text + '\n')

def save_img_from_word(filename, folder_save_img = 'images'):
  # Delete folder if exists
  from shutil import rmtree
  if os.path.exists(folder_save_img):
    rmtree(folder_save_img)
  
  from docx2txt import process
  # Create folder if not exists
  if not os.path.exists(folder_save_img):
    os.makedirs(folder_save_img)

  # Save images from word file
  
  text = process(filename, folder_save_img)

  return

def get_heading_word_file(filename):
  lheading = []
  doc = docx.Document(filename)
  
  # Get all heading 2
  for para in doc.paragraphs:
    if para.style.name == 'Heading 2':
      lheading.append(para.text)

  return lheading

def count_files(directory):
    count = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            count += 1
    return count

def photo_handler(update, context):
    # Lấy hình ảnh từ tin nhắn của người dùng
    photo = update.message.photo[-1]

    # Lấy thông tin của tệp tin ảnh
    file = context.bot.get_file(photo.file_id)

    # Lấy đường dẫn đến tệp tin ảnh
    file_path = file.file_path
    
    # Lấy dữ liệu của hình ảnh từ đường dẫn tệp tin ảnh
    image_data = requests.get(file_path).content

    update.message.reply_text('Đã nhận được ảnh!')

def docx_handler(update, context):
  try:
    # Lấy thông tin về file đính kèm
    file = context.bot.get_file(update.message.document.file_id)
    filepath = file.file_path

    # Kiểm tra xem tên file có kết thúc bằng '.docx' hay không
    if filepath.endswith('.docx'):
      # Tải file xuống và lưu nó
      response = requests.get(filepath)
      with open(docx_name, "wb") as f:
          f.write(response.content)
      
      # Lưu file docx và set event cho thông báo load file
      event_changeword.set()
      update.message.reply_text('Đã lưu file docx!')
      
    else:
        # Nếu không, trả lời tin nhắn
        update.message.reply_text("File không hợp lệ. Vui lòng gửi file định dạng .docx")
  
  except Exception as e:
    print("Exception: ", e)
    update.message.reply_text("Exception docx: " + str(e))

def notify_handle(update, context):
  update.message.reply_text('Xin chào!')
  chat_id = update.message.chat_id
  #print("chat_id_notify: ", chat_id)
  #context.job_queue.run_once(schedule_notify, 1, context=chat_id)

def schedule_notify(bot):
  # Gửi tin nhắn đến 1 người dùng
  # chat_id = context.job.context

  chat_id = 1042979764
  id_img_old = 0
  event_changeword.set()
  while 1:
    try:
      if event_changeword.is_set():
        # Read file docx if exists
        event_changeword.clear()
        if os.path.exists(docx_name):
          print("Reading docx...")
          save_img_from_word(docx_name)
        else:
          bot.send_message(chat_id=chat_id, text="Không tìm thấy file docx!")
          event_changeword.wait(wait_time)
          continue

      # Count img
      numof_img = count_files('images')

      # Send img
      if numof_img >= 4:
        while True:
          num = random.choice(list(range(1, numof_img, 2)))
          if num != id_img_old:
            break
        id_img_old = num

        # Send to bot
        now = datetime.datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))
        bot.send_message(chat_id=chat_id, text=f'Time: {now.strftime("%Y-%m-%d %H:%M:%S")}')
        bot.send_photo(chat_id=chat_id, photo=open(f'images\image{num}.png', 'rb'))
        bot.send_photo(chat_id=chat_id, photo=open(f'images\image{num+1}.png', 'rb'))
      else:
        bot.send_message(chat_id=chat_id, text="Chưa đủ hình ảnh!")
      
      # Time sleep
      print(f"Sleeping {wait_time} seconds...")
      event_changeword.wait(wait_time)

    except Exception as e:
      bot.send_message(chat_id=chat_id, text="Exception: " + str(e))
      time.sleep(wait_time)



def main():
  token = "6179912911:AAGMg3od1lNvVQunmpyWRkUOe77mkjNWa1s" # anhdz_fxexp_bot
  updater = Updater(token=token, use_context=True)
  dispatcher = updater.dispatcher

  # start handle
  # start_handler = CommandHandler('notify', notify_handle)
  # dispatcher.add_handler(start_handler)

  # handle message to image
  dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
  dispatcher.add_handler(MessageHandler(Filters.document, docx_handler))

  updater.start_polling()
  print("Bot is running...")

  # thread send notify
  thread = threading.Thread(target=schedule_notify, args=(updater.bot,))
  thread.daemon = True
  thread.start()

  updater.idle()
# Main
if __name__ == "__main__":
  main()
  pass
