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


if Config.SAVE_TO_DATABASE:
    db = Database()
    CREDIT = Config.CREDIT


############Variables##############
IST = timezone('Asia/Kolkata')
User_Data = Config.User_Data
botStartTime = time()


############Helper Functions##############
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


def time_formatter(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (((str(days) + "d, ") if days else "") +
           ((str(hours) + "h, ") if hours else "") +
           ((str(minutes) + "m, ") if minutes else "") +
           ((str(seconds) + "s, ") if seconds else "") +
           ((str(milliseconds) + "ms, ") if milliseconds else ""))
    return tmp[:-2]


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

##########Save Token###############
def USER_DATA():
    return User_Data

#########gen data###########
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


##########Save Token###############
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
    
##########options###############
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
    
##########Save Restart Message Id###############
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
    

##########Clear Restart Message Id###############
async def clear_restart():
    try:
        User_Data['restart'] = []
        await db.add_datam(str(User_Data), CREDIT, "User_Data")
        return
    except Exception as e:
        print(e)
        return False

##########Delete Token###############
async def deleteconfig(user_id, dname, pos):
        try:
            del User_Data[user_id][dname][pos]
            data = await db.add_datam(str(User_Data), CREDIT, "User_Data")
            return data
        except Exception as e:
            print(e)
            return False

##########Clean##########
async def delete_trash(file):
    try:
        remove(file)
    except:
        pass
    return

######Delete Folder##########
async def delete_all(dir):
    try:
        rmtree(dir)
    except:
        pass
    return

########Background#############
async def create_backgroud_task(x):
    task = get_event_loop().create_task(x)
    return task


#########Process FFmpeg##########
async def create_process_file(file):
    if exists(file):
        remove(file)
    with open(file, 'w') as fp:
            pass
    return

#######Make Dir############
async def make_direc(direc):
    try:
        if not isdir(direc):
            mkdir(direc)
    except:
        pass
    return direc


#######get media duration######
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


#######cleartrashlist########
async def clear_trash_list(trash_list):
    for t in trash_list:
            try:
                remove(t)
                trash_list.remove(t)
            except:
                pass
    return


######Bot Stats###########
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
    

#########check file########
async def check_file_exists(file):
    if exists(file):
        return True
    else:
        return False
    

#########check files########
async def check_files_exists(files):
    for file in files:
        if not exists(file):
            return False
    return True

#########process checker########
async def process_checker(check_data):
    for data in check_data:
        if data[0] not in data[1]:
            return False
    return True



########get stream output#######
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


#########Compress Details########
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

######Get Rclone Config##########
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

#########Get Current Time##########
def get_current_time():
    return str(datetime.now(IST).strftime('%I:%M:%S %p (%d-%b)'))
