from os import getenv
from telethon import TelegramClient
from pymongo import MongoClient
from logging import StreamHandler, getLogger, basicConfig, ERROR, DEBUG, INFO
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from os.path import exists
from telethon.sessions import StringSession

if exists('config.env'):
  load_dotenv('config.env')
  
  
if exists("Logging.txt"):
    with open("Logging.txt", "r+") as f_d:
        f_d.truncate(0)


basicConfig(
    level=INFO,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "Logging.txt", maxBytes=50000000, backupCount=10, encoding="utf-8"
        ),
        StreamHandler(),
    ],
)
getLogger("telethon").setLevel(ERROR)


        
        
def get_mongo_data(MONGODB_URI, BOT_USERNAME, id, colz):
        mongo_client = MongoClient(MONGODB_URI)
        mongo_db = mongo_client[BOT_USERNAME]
        col = mongo_db[colz]
        print("🔶Getting Data From Database")
        item_details = col.find({"id" : id})
        data = False
        for item in item_details:
                        data = item.get('data')
        if data:
            print("🟢Data Found In Database")
            return data
        else:
            print("🟡Data Not Found In Database")
            return "{}"


class Config:
    API_ID = int(getenv("API_ID",""))
    API_HASH = getenv("API_HASH","")
    TOKEN = getenv("TOKEN","")
    Session_String = getenv("Session_String","")
    client = TelegramClient("Nik66TestBot", API_ID, API_HASH)
    Use_Session_String = getenv("Use_Session_String","")
    if Use_Session_String=="True":
        USER = TelegramClient(StringSession(Session_String), API_ID, API_HASH)
    else:
        USER = False
    SUDO_USERS = eval(getenv("SUDO_USERS",""))
    SAVE_TO_DATABASE = eval(getenv("SAVE_TO_DATABASE",""))
    if SAVE_TO_DATABASE:
        MONGODB_URI = getenv("MONGODB_URI","")
        CREDIT = getenv("CREDIT","")
        BOT_USERNAME = getenv("BOT_USERNAME","")
        User_Data = eval(get_mongo_data(MONGODB_URI, BOT_USERNAME, CREDIT, "User_Data"))
    else:
        User_Data = {}
    LOGGER = getLogger()
    try:
        RESTART_NOTIFY_ID = int(getenv("RESTART_NOTIFY_ID",""))
    except:
        RESTART_NOTIFY_ID = False