from config import Config
from db_handler import Database
from time import time
from os import remove, mkdir
from shutil import rmtree
from asyncio import get_event_loop
from os.path import exists, isdir
from subprocess import PIPE as subprocessPIPE, STDOUT as subprocessSTDOUT
from subprocess import run as subprocessrun
from psutil import disk_usage, cpu_percent,virtual_memory
from shlex import split as shlexsplit
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from typing import Tuple
from configparser import ConfigParser
from datetime import datetime
from pytz import timezone
from string import ascii_lowercase, digits
from random import choices



#////////////////////////////////////Variables////////////////////////////////////#
if Config.SAVE_TO_DATABASE:
    db = Database()
    CREDIT = Config.CREDIT
IST = timezone('Asia/Kolkata')
User_Data = Config.User_Data
botStartTime = time()



#////////////////////////////////////Database////////////////////////////////////#

###############------Return_Database------###############
def USER_DATA():
    return User_Data

###############------New_User------###############
async def new_user(user_id, dbsave):
        User_Data[user_id] = {}
        User_Data[user_id]['watermark'] = {}
        User_Data[user_id]['watermark']['position'] = '5:5'
        User_Data[user_id]['watermark']['size'] = '7'
        User_Data[user_id]['watermark']['crf'] = '23'
        User_Data[user_id]['watermark']['use_crf'] = False
        User_Data[user_id]['watermark']['encode'] = True
        User_Data[user_id]['watermark']['encoder'] = 'libx265'
        User_Data[user_id]['watermark']['preset'] = 'ultrafast'
        User_Data[user_id]['watermark']['map_audio'] = True
        User_Data[user_id]['watermark']['map_sub'] = True
        User_Data[user_id]['watermark']['map'] = True
        User_Data[user_id]['muxer'] = {}
        User_Data[user_id]['muxer']['preset'] = 'ultrafast'
        User_Data[user_id]['muxer']['use_crf'] = False
        User_Data[user_id]['muxer']['crf'] = '23'
        User_Data[user_id]['muxer']['map_audio'] = True
        User_Data[user_id]['muxer']['map_sub'] = True
        User_Data[user_id]['muxer']['map'] = True
        User_Data[user_id]['muxer']['encode'] = True
        User_Data[user_id]['muxer']['encoder'] = 'libx265'
        User_Data[user_id]['compress'] = {}
        User_Data[user_id]['compress']['preset'] = 'ultrafast'
        User_Data[user_id]['compress']['crf'] = '23'
        User_Data[user_id]['compress']['map_audio'] = True
        User_Data[user_id]['compress']['map_sub'] = True
        User_Data[user_id]['compress']['map'] = True
        User_Data[user_id]['compress']['copy_sub'] = False
        User_Data[user_id]['compress']['encoder'] = 'libx265'
        User_Data[user_id]['compression'] = False
        User_Data[user_id]['select_stream'] = False
        User_Data[user_id]['stream'] = 'ENG'
        User_Data[user_id]['split_video'] = False
        User_Data[user_id]['split'] = '2GB'
        User_Data[user_id]['upload_tg'] = True
        User_Data[user_id]['rclone'] = False
        User_Data[user_id]['drive_name'] = False
        User_Data[user_id]['merge'] = {}
        User_Data[user_id]['merge']['map_audio'] = True
        User_Data[user_id]['merge']['map_sub'] = True
        User_Data[user_id]['merge']['map'] = True
        User_Data[user_id]['custom_thumbnail'] = False
        User_Data[user_id]['convert_video'] = False
        User_Data[user_id]['convert_quality'] = [720, 480]
        User_Data[user_id]['convert'] = {}
        User_Data[user_id]['convert']['preset'] = 'ultrafast'
        User_Data[user_id]['convert']['use_crf'] = False
        User_Data[user_id]['convert']['crf'] = '23'
        User_Data[user_id]['convert']['map'] = True
        User_Data[user_id]['convert']['encode'] = True
        User_Data[user_id]['convert']['encoder'] = 'libx265'
        User_Data[user_id]['custom_name'] = False
        User_Data[user_id]['custom_metadata'] = False
        User_Data[user_id]['metadata'] = "Nik66Bots"
        User_Data[user_id]['detailed_messages'] = True
        User_Data[user_id]['show_stats'] = True
        User_Data[user_id]['show_botuptime'] = True
        User_Data[user_id]['update_time'] = 7
        User_Data[user_id]['ffmpeg_log'] = True
        User_Data[user_id]['ffmpeg_size'] = True
        User_Data[user_id]['ffmpeg_ptime'] = True
        User_Data[user_id]['auto_drive'] = False
        User_Data[user_id]['show_time'] = True
        User_Data[user_id]['gen_ss'] = True
        User_Data[user_id]['ss_no'] = 5
        if dbsave:
            data = await db.add_datam(str(User_Data), CREDIT, "User_Data")
        else:
            data = True
        return data

###############------Save_Config------###############
async def saveoptions(user_id, dname, value, dbsave):
    try:
        if user_id not in User_Data:
            User_Data[user_id] = {}
            User_Data[user_id][dname] = {}
            User_Data[user_id][dname] = value
        else:
            User_Data[user_id][dname] = value
        if dbsave:
            data = await db.add_datam(str(User_Data), CREDIT, "User_Data")
        else:
            data = True
        return data
    except Exception as e:
        print(e)
        return False
    
###############------Save_Sub_Config------###############
async def saveconfig(user_id, dname, pos, value, dbsave):
    try:
        if user_id not in User_Data:
            User_Data[user_id] = {}
            User_Data[user_id][dname] = {}
            User_Data[user_id][dname][pos] = value
        else:
            User_Data[user_id][dname][pos] = value
        if dbsave:
            data = await db.add_datam(str(User_Data), CREDIT, "User_Data")
        else:
            data = True
        return data
    except Exception as e:
        print(e)
        return False

###############------Save_Restart_IDs------###############
async def save_restart(chat_id, msg_id):
    try:
        if 'restart' not in User_Data:
            User_Data['restart'] = []
            User_Data['restart'].append([chat_id, msg_id])
        else:
            User_Data['restart'].append([chat_id, msg_id])
        await db.add_datam(str(User_Data), CREDIT, "User_Data")
        return
    except Exception as e:
        print(e)
        return False
    
###############------Clear_Restart_IDs------###############
async def clear_restart():
    try:
        User_Data['restart'] = []
        await db.add_datam(str(User_Data), CREDIT, "User_Data")
        return
    except Exception as e:
        print(e)
        return False


#////////////////////////////////////Functions////////////////////////////////////#

###############------Time_Functions------###############
def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


class Timer:
    def __init__(self, time_between=5):
        self.start_time = time()
        self.time_between = time_between

    def can_send(self):
        if time() > (self.start_time + self.time_between):
            self.start_time = time()
            return True
        return False

def get_time():
    return time()


def getbotuptime():
    return get_readable_time(time() - botStartTime)


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


def get_current_time():
    return str(datetime.now(IST).strftime('%I:%M:%S %p (%d-%b)'))


###############------Size_Functions------###############
def get_human_size(num):
    base = 1024.0
    sufix_list = ['B','KB','MB','GB','TB','PB','EB','ZB', 'YB']
    for unit in sufix_list:
        if abs(num) < base:
            return f"{round(num, 2)} {unit}"
        num /= base

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def hrb(value, digits= 2, delim= "", postfix=""):
    """Return a human-readable file size.
    """
    if value is None:
        return None
    chosen_unit = "B"
    for unit in ("KB", "MB", "GB", "TB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix


#////////////////////////////////////File_System_Functions////////////////////////////////////#

###############------Delete_File------###############
async def delete_trash(file):
    try:
        remove(file)
    except:
        pass
    return

###############------Delete_Directory------###############
async def delete_all(dir):
    try:
        rmtree(dir)
    except:
        pass
    return


###############------Create_Progress_File------###############
async def create_process_file(file):
    if exists(file):
        remove(file)
    with open(file, 'w') as fp:
            pass
    return

###############------Make_Directory------###############
async def make_direc(direc):
    try:
        if not isdir(direc):
            mkdir(direc)
    except:
        pass
    return direc


###############------Check_File_Exists------###############
async def check_file_exists(file):
    if exists(file):
        return True
    else:
        return False
    

###############------Check_Files_Exists------###############
async def check_files_exists(files):
    for file in files:
        if not exists(file):
            return False
    return True


###############------Get_Logs_From_File------###############
def get_logs_msg(log_file):
    with open(log_file, 'r', encoding="utf-8") as f:
                logFileLines = f.read().splitlines()
                Loglines = ''
                ind = 1
                while len(Loglines) <= 3000:
                    Loglines = logFileLines[-ind]+'\n'+Loglines
                    if ind == len(logFileLines): break
                    ind += 1
                startLine = f"Generated Last {ind} Lines from {str(log_file)}: \n\n---------------- START LOG -----------------\n\n"
                endLine = "\n---------------- END LOG -----------------"
                return startLine+Loglines+endLine


###############------Clear_Trash_List------###############
async def clear_trash_list(trash_list):
    for t in trash_list:
            try:
                remove(t)
                trash_list.remove(t)
            except:
                pass
    return


#////////////////////////////////////Commands////////////////////////////////////#

###############------Create_Background_Task------###############
async def create_backgroud_task(x):
    task = get_event_loop().create_task(x)
    return task



###############------Get_Media_Duration------###############
def get_video_duration(filename):
    result = subprocessrun(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocessPIPE,
        stderr=subprocessSTDOUT)
    try:
        duration = int(float(result.stdout))
    except:
        duration = 0
    return duration



###############------Get_Process_Output------###############
async def execute(cmnd: str) -> Tuple[str, str, int, int]:
    print(cmnd)
    cmnds = shlexsplit(cmnd)
    process = await create_subprocess_exec(
        *cmnds,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode('utf-8', 'replace').strip()



#////////////////////////////////////Other_Functions////////////////////////////////////#


###############------Rclone_Accounts------###############
async def get_config(file):
    try:
        config = ConfigParser(default_section=False)
        config.read(file, encoding="utf-8")
        accounts = []
        for d in config:
            if d:
                accounts.append(str(d))
        if len(accounts):
            return accounts
        else:
            return False
    except Exception as e:
        print(e)
        return False


###############------Generate_Random_String------###############
def gen_random_string(k):
    return str(''.join(choices(ascii_lowercase + digits, k=k)))


###############------Check_Process------###############
async def process_checker(check_data):
    for data in check_data:
        if data[0] not in data[1]:
            return False
    return True


###############------Get_Bot_Stats------###############
def get_stats(userx):
        if User_Data[userx]['show_stats']:
            total, used, free, disk = disk_usage('/')
            memory = virtual_memory()
            stats =f'🚀CPU Usage: {cpu_percent(interval=0.5)}%\n'\
                        f'⚡RAM Usage: {memory.percent}%\n'\
                        f'🚛Total Space: {get_human_size(total)}\n'\
                        f'🧡Free Space: {get_human_size(free)}\n'\
                        f'🚂Total Ram: {get_human_size(memory.total)}\n'\
                        f'⚓Free Ram: {get_human_size(memory.available)}'
        else:
            stats =f'🚀CPU Usage: {cpu_percent(interval=0.5)}%'
        return stats


###############------Detailed_Message------###############
def get_details(pmode, userx, head):
    if User_Data[userx]['detailed_messages']:
        if pmode=="compress":
            compress_encoder = User_Data[userx]['compress']['encoder']
            compress_preset = User_Data[userx]['compress']['preset']
            compress_crf = User_Data[userx]['compress']['crf']
            compress_map = User_Data[userx]['compress']['map']
            compress_copysub = User_Data[userx]['compress']['copy_sub']
            text =f'🍬Encoder: {compress_encoder}\n'\
                            f'♒Preset: {compress_preset}\n'\
                            f'⚡CRF: {compress_crf}\n'\
                            f'🍓Map: {compress_map}\n'\
                            f'🍄Copy Subtitles: {compress_copysub}'
            if head:
                text = f'Compression Settings:\n{text}'
            else:
                text = f'🍫Mode: Compression\n{text}'
            return text
    else:
        return False