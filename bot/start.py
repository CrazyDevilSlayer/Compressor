from config import Config
from telethon import events, Button
from time import time
from helper_fns.Helper import get_readable_time, USER_DATA, getbotuptime, new_user, get_video_duration, get_details, Timer, make_direc, clear_trash_list, process_checker, get_time, execute, get_config, saveoptions, delete_trash, get_human_size, save_restart
from helper_fns.Ruunung_Process import append_master_process, remove_master_process, get_master_process, append_sub_process, remove_sub_process, get_sub_process
from helper_fns.Progress_Bar import progress_bar
from string import ascii_lowercase, digits
from random import choices
from telethon.tl.types import DocumentAttributeVideo
from helper_fns.Fast_Telethon import upload_file, download_file
from helper_fns.Video_Engine import Processor
from json import loads
from helper_fns.FFMPEG_Engine import run_process_command
from os.path import getsize, exists
from re import escape, findall
from helper_fns.FFMPEG_Engine import upload_rclone
from aiohttp import ClientSession
from asyncio import sleep as asynciosleep
from aiofiles import open as aiofiles_open
from os import remove
from os import execl
from sys import argv, executable
# from hachoir.metadata import extractMetadata
# from hachoir.parser import createParser



############Variables##############
sudo_users = Config.SUDO_USERS
Client = Config.client
USER = Config.USER
LOGGER = Config.LOGGER
queue = {}
punc = ['!', '|', '{', '}', ';', ':', "'", '=', '"', '\\', ',', '<', '>', '/', '?', '@', '#', '$', '%', '^', '&', '*', '~', "  ", "\t", "+", "b'", "'"]
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE


###########Functions################
def get_mention(event):
    return "["+event.message.sender.first_name+"](tg://user?id="+str(event.message.sender.id)+")"


########Logs MSG################
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

async def download_tg_file(new_event, download_location, reply, datam, check_data, userx):
        start_time = time()
        timer = Timer(USER_DATA()[userx]['update_time'])
        try:
            with open(download_location, "wb") as f:
                    await download_file(
                        client=Client, 
                        location=new_event.message.document, 
                        out=f,
                        check_data=check_data,
                        progress_callback=lambda x,y: progress_bar(x,y,reply,start_time,datam, userx, timer))
        except Exception as e:
                if str(e)=="Cancelled":
                        await reply.edit("✅Task Cancelled")
                else:
                    await reply.edit(str(e))
                    LOGGER.info(str(e))
                return False
        return True

async def get_file_details_url(url):
    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                status = response.status
                if status==200:
                    valid = True
                else:
                    return [False, False]
                headers =response.headers
                d = headers.get("Content-Disposition")
                file_name = False
                if d:
                    try:
                        file_name = findall("filename=(.+)", d)[0].replace("'", "").replace('"', '').strip()
                    except Exception as e:
                        LOGGER.info(str(e))
                        print(e)
                return [valid, file_name]
    except Exception as e:
        LOGGER.info(str(e))
        print(e)
        return [False, False]


async def download_coroutine(session, url, userx, dl_loc, reply, check_data, datam, retry):
    CHUNK_SIZE = 1024 * 6  # 2341
    downloaded = 0
    start = time()
    timer = Timer(USER_DATA()[userx]['update_time'])
    Cancel = False
    await delete_trash(dl_loc)
    async with session.get(url) as response:
        try:
            total_length = int(response.headers["Content-Length"])
            content_type = response.headers["Content-Type"]
            if "text" in content_type and total_length < 500:
                await response.release()
                await reply.edit("❗Error: Got Text From Link")
                return False
            async with aiofiles_open(dl_loc, 'wb') as f_handle:
                while True:
                    chunk = await response.content.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    checker = await process_checker(check_data)
                    if not checker:
                            await reply.edit("🔒Task Cancelled By User")
                            Cancel = True
                            break
                    await f_handle.write(chunk)
                    downloaded += CHUNK_SIZE
                    if total_length-downloaded>0:
                        await progress_bar(downloaded,total_length,reply, start, datam, userx, timer)
            await response.release()
            if Cancel:
                    return False
            else:
                    return True
        except Exception as e:
            if retry==0:
                await reply.edit(f"❗Error: {str(e)}")
                LOGGER.info(str(e))
                return False
            else:
                return await download_coroutine(session, url, userx, dl_loc, reply, check_data, datam, retry-1)

async def upload_tg_video(tgclient, user_id, userx,  event, files, caption, reply, datam, check_data, thumbnail):
    total_files = len(files)
    if USER_DATA()[userx]['upload_tg']:
            # try:
            #         metadata = extractMetadata(createParser(fileloc))
            #         duration = int(metadata.get('duration').seconds)
            # except Exception as e:
            #     print(e)
            #     duration = 0
            for i in range(len(files)):
                start_time = time()
                timer = Timer(USER_DATA()[userx]['update_time'])
                duration = get_video_duration(files[i])
                attributes=(DocumentAttributeVideo(duration, 0, 0),)
                filename = str(files[i].split("/")[-1]).replace(".VideoFlux", "").replace("VideoFlux", "")
                caption = f"{filename}\n\n" + str(caption).strip()
                datam[1] = f"🔼Uploading [{str(i+1)}/{str(total_files)}]"
                with open(files[i], "rb") as f:
                    ok = await upload_file(
                        client=tgclient,
                        file=f,
                        name=filename,
                        check_data=check_data,
                        progress_callback=lambda x,y: progress_bar(x,y,reply,start_time,datam, userx, timer))
                await tgclient.send_file(user_id, file=ok, thumb=thumbnail, allow_cache=False, supports_streaming=True, caption=caption, reply_to=event.message, attributes=attributes)
            return

async def init_user(event, userx):
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return False
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    return True


async def generate_screenshoot(ss_time, input_video, ss_name):
    command = [
        "ffmpeg",
        "-ss",
        str(ss_time),
        "-i",
        input_video,
        "-frames:v",
        "1",
        "-f",
        "image2",
        "-map",
        "0:v:0",
        "-y",
        ss_name
    ]
    return await run_process_command(command)


async def gen_ss_list(duration, ss_no):
    value = round(duration/ss_no)
    ss_list = [5]
    ss = 5
    while True:
        ss = ss+value
        if len(ss_list)==ss_no:
            break
        if ss<duration:
            ss_list.append(ss)
        else:
            ss_list.append(duration-2)
            break
    return ss_list


async def send_ss(event, user_id, userx, duration, input_video, file_name, work_loc):
    if USER_DATA()[userx]['gen_ss']:
        ss_n0 = USER_DATA()[userx]['ss_no']
        ss_list = await gen_ss_list(duration, ss_n0)
        sn0 = 1
        for ss_time in ss_list:
            ss_name = f"{work_loc}/{file_name}_{str(time())}.jpg"
            ssresult = await generate_screenshoot(ss_time, input_video, ss_name)
            if ssresult and exists(ss_name):
                sscaption = f"📌 Position: {str(get_readable_time(ss_time))}\n📷 Screenshot: {str(sn0)}/{str(ss_n0)}"
                try:
                    await Client.send_file(user_id, file=ss_name, allow_cache=False, reply_to=event.message, caption=sscaption)
                except:
                    pass
                remove(ss_name)
                sn0+=1
                await asynciosleep(1)
        return

async def get_dw_type(new_event):
    try:
        if new_event.message.media:
            return ["tg", False]
        else:
            return ["url", False]
    except:
        return ["tg", False]
    

async def get_url_from_message(new_event):
        if new_event.message.file:
            return False
        else:
            return str(new_event.message.message)

async def add_queue(process, userx, new_event, url_download, file_loc, file_name, ext, thumbnail):
    queue_data = {}
    queue_data['event'] = new_event
    queue_data['url_download'] = url_download
    queue_data['process'] = process
    queue_data[' file_loc'] =  file_loc
    queue_data['file_name'] = file_name
    queue_data['ext'] = ext
    queue_data['thumbnail'] = thumbnail
    queue[userx]['tasks'].append(queue_data)
    return


async def get_ext(event):
    if "|" in event.message.message:
        ext = str(event.message.message.split('|')[-1]).replace('.', '').strip()
    else:
        ext = False
    return ext


async def ask_media(event, user_id, userx, detailed_message, keywords, message, timeout, mtype, queue_task):
    async with Client.conversation(user_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: e.message.file or str(e.message.message) in keywords or str(e.message.message).startswith("http")), timeout=timeout)
            if not queue_task:
                msg = f"*️⃣ {str(message)} [{str(timeout)} secs]"
            else:
                msg = f"*️⃣ {str(message)} [{str(timeout)} secs]\n\n#️⃣Task Queuing Is ON\n🔶Queued Tasks : {str(len(queue[userx]['tasks']))}"
            if not detailed_message:
                ask = await event.reply(msg)
            else:
                ask = await event.reply(f'{msg} \n\n{str(detailed_message)}')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(str(e))
                return False
            if new_event.message.file:
                if not str(new_event.message.file.mime_type).startswith(mtype):
                    await new_event.reply(f'❗[{str(new_event.message.file.mime_type)}] This is not a valid file.')
                    return False
                return new_event
            elif new_event.message.message:
                if str(new_event.message.message)=='stop':
                    await ask.reply('✅Task Stopped')
                    return "cancelled"
                elif str(new_event.message.message)=='pass':
                    await ask.reply('✅Task Passed')
                    return "passed"
                elif str(new_event.message.message).startswith("http"):
                    return new_event
                else:
                    await ask.reply(f'❗You already started a task, now send {str(new_event.message.message)} command again.')
                    return "cancelled"


async def get_filename(event, user_id, userx, process_id, ext, detailed_message, timeout, loc, check, url):
    loc = await make_direc(f'{str(userx)}_{str(loc)}')
    if check:
        custom_name = True
    else:
        custom_name = USER_DATA()[userx]['custom_name']
    if url:
        valid, filename = await get_file_details_url(url)
        if not valid:
            await event.reply(f'❗Falied To Connect URL.')
            return False
    if not custom_name:
        if not url:
            if event.message.file:
                    filename = event.message.file.name
            else:
                    filename = process_id
        if filename:
            if "." in filename:
                    try:
                        ext = str(filename.split(".")[-1]).strip()
                    except:
                        pass
    else:
        async with Client.conversation(user_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: e.message.message), timeout=timeout)
            if not detailed_message:
                ask = await event.reply(f'*️⃣ Send File Name|Extenstion\n(e.g. DBZE01|mkv) [{str(timeout)} secs]')
            else:
                ask = await event.reply(f'*️⃣ Send File Name|Extenstion\n(e.g. DBZE01|mkv) [{str(timeout)} secs] \n\n{str(detailed_message)}')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                print(e)
                LOGGER.info(str(e))
                return False
            if "|" in new_event.message.message:
                data = new_event.message.message.split("|")
                filename = data[0]
                if len(data)>1:
                    ext = data[-1]
            else:
                filename = new_event.message.message
    try:
        for ele in punc:
            if ele in filename:
                    filename = filename.replace(ele, '')
    except:
        filename = process_id
        
    if not ext:
        async with Client.conversation(user_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: e.message.message), timeout=timeout)
            if not detailed_message:
                ask = await event.reply(f'*️⃣ Send File Extenstion [{str(timeout)} secs]')
            else:
                ask = await event.reply(f'*️⃣ Send File Extenstion [{str(timeout)} secs] \n\n{str(detailed_message)}')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                print(e)
                LOGGER.info(str(e))
                return False
            ext = str(new_event.message.message).replace('.', '').strip()
    if str(filename).endswith(f".{str(ext)}"):
        return [f"{str(loc)}/{str(filename)}", str(filename), str(ext)]
    else:
        return [f"{str(loc)}/{str(filename)}.{str(ext)}", f"{str(filename)}.{str(ext)}", str(ext)]


async def select_audio(new_event, userx, input_file, caption):
                                        select_stream = USER_DATA()[userx]['select_stream']
                                        language = USER_DATA()[userx]['stream']
                                        amap_options = '0:a'
                                        if select_stream:
                                                try:
                                                        get_streams = await execute(f"ffprobe -hide_banner -show_streams -print_format json '{input_file}'")
                                                        details = loads(get_streams)
                                                        stream_data = {}
                                                        smsg = ''
                                                        for stream in details["streams"]:
                                                                stream_name = stream["codec_name"]
                                                                stream_type = stream["codec_type"]
                                                                codec_long_name = stream['codec_long_name']
                                                                if stream_type in ("audio"):
                                                                        mapping = stream["index"]
                                                                        try:
                                                                                lang = stream["tags"]["language"]
                                                                        except:
                                                                                lang = mapping
                                                                        sname = f"{stream_type.upper()} - {str(lang).upper()} [{codec_long_name}]"
                                                                        stream_data[sname] = {}
                                                                        stream_data[sname]['index'] =mapping
                                                                        stream_data[sname]['language'] = str(lang).upper()
                                                                        smsg+= f'`{sname}`\n\n'
                                                        if len(stream_data)==0:
                                                                await new_event.reply("❗Failed To Find Audio Streams From Video")
                                                                return [amap_options, caption]
                                                        elif len(stream_data)==1:
                                                                await new_event.reply("🔶Only One Audio Found In The Video So Skipping Audio Select.")
                                                                return [amap_options, caption]
                                                        else:
                                                                skeys = list(stream_data.keys())
                                                                for k in skeys:
                                                                        if stream_data[k]['language']==language:
                                                                                cstream = k
                                                                                stream_no = stream_data[cstream]['index']
                                                                                amap_options = f'0:a:{str(int(stream_no)-1)}'
                                                                                await new_event.reply(f'✅Audio Selected Successfully\n\n`{str(cstream)}`\nStream No: {str(stream_no)}')
                                                                                caption += f"✅Audio: {str(cstream)}"
                                                                                return [amap_options, caption]
                                                                await new_event.reply(f'❗{language} Language Not Found In Video.')
                                                                return [amap_options, caption]
                                                except Exception as e:
                                                        LOGGER.info(str(e))
                                                        await new_event.reply(f"❌Failed To Get Audio Streams From Video\n\n{str(e)}")
                                                        return [amap_options, caption]
                                        else:
                                            return [amap_options, caption]
                                        
async def change_metadata(new_event, userx, dl_loc, filename, ext, caption):
    if USER_DATA()[userx]['custom_metadata']:
            output_meta = str(dl_loc).replace(ext, f"VideoFlux.{ext}")
            custom_metadata_title = USER_DATA()[userx]['metadata']
            cmd_meta = ["ffmpeg", "-i", f"{dl_loc}", f"-metadata:s:a", f"title={custom_metadata_title}", f"-metadata:s:s", f"title={custom_metadata_title}", "-map", "0", "-c", "copy", '-y', f"{output_meta}"]
            met_result = await run_process_command(cmd_meta)
            if not met_result:
                    cmd_meta = ["ffmpeg", "-i", f"{dl_loc}", f"-metadata:s:a", f"title={custom_metadata_title}", "-map", "0", "-c", "copy", '-y', f"{output_meta}"]
                    met_result = await run_process_command(cmd_meta)
            if not met_result:
                    cmd_meta = ["ffmpeg", "-i", f"{dl_loc}", f"-metadata:s:s", f"title={custom_metadata_title}", "-map", "0", "-c", "copy", '-y', f"{output_meta}"]
                    met_result = await run_process_command(cmd_meta)
            if met_result:
                    await new_event.reply(f"✅Metadata Set Successfully")
                    caption+= f"\n✅Metadata: {custom_metadata_title}"
                    return [output_meta, filename, ext, caption]
            else:
                    await new_event.reply(f"❗Failed To Set MetaData")
                    return [dl_loc, filename, ext, caption]
    else:
        return [dl_loc, filename, ext, caption]
    

async def get_thumbnail(event, user_id, userx, loc,  filename, detailed_message, keywords, timeout):
    thumb = './thumb.jpg'
    if USER_DATA()[userx]['custom_thumbnail']:
        async with Client.conversation(user_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: e.message.media or str(e.message.message) in keywords), timeout=timeout)
            if not detailed_message:
                ask = await event.reply(f'*️⃣ Send Thumbnail [{str(timeout)} secs]')
            else:
                ask = await event.reply(f'*️⃣ Send Thumbnail [{str(timeout)} secs] \n\n{str(detailed_message)}')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Task Has Been Cancelled.')
                LOGGER.info(str(e))
                return thumb
            if new_event.message.media:
                if not str(new_event.message.file.mime_type).startswith('image/'):
                    await new_event.reply(f'❗[{str(new_event.message.file.mime_type)}] This is not a valid thumbnail.')
                    return thumb
            elif new_event.message.message:
                if str(new_event.message.message)=='pass':
                    await ask.reply('✅Task Passed')
                    return thumb
                else:
                    await ask.reply(f'❗You already started a task, now send {str(new_event.message.message)} command again.')
                    return False
            loc = await make_direc(f'{str(userx)}_{str(loc)}')
            custom_thumb = f"{str(loc)}/{str(filename)}.jpg"
            await Client.download_media(new_event.message, custom_thumb)
            return custom_thumb
    else:
        return thumb
    
async def check_size_limit():
        size = 2097151000
        if USER:
                user = await USER.get_me()
                if user.premium:
                    size = 4194304000
        return size


async def get_split_size(userx):
    if USER_DATA()[userx]['upload_tg']:
            if USER_DATA()[userx]['split']=='2GB':
                split_size = 2097151000
            else:
                split_size = await check_size_limit()
            return split_size
    else:
        return False

async def files_size_check(files, size):
    for f in files:
        if getsize(f)>size:
            return False
    return True


async def upload_drive(event, user_id, reply, caption, userx, r_config, final_files, datam, check_data):
                        total = len(final_files)
                        q = 1
                        for output_vid in final_files:
                                file_name = output_vid.split("/")[-1].replace(".VideoFlux", "").replace("VideoFlux", "")
                                caption = f"{file_name}\n\n" + str(caption).strip()
                                datam[0] = file_name
                                datam[1] = f'❣Uploading To Drive[{str(q)}/{str(total)}]'
                                try:
                                        drive_name = USER_DATA()[userx]['drive_name']
                                        command =  [ "rclone",
                                                                        "copy",
                                                                        f"--config={r_config}",
                                                                        f'{str(output_vid)}',
                                                                        f'{drive_name}:/',
                                                                        "-f",
                                                                        "- *.!qB",
                                                                        "--buffer-size=1M",
                                                                        "-P",
                                                                ]
                                        search_command =  [
                                                        "rclone",
                                                        "lsjson",
                                                        f"--config={r_config}",
                                                        f'{drive_name}:/',
                                                        "--files-only",
                                                        "-f",
                                                        f"+ {escape(file_name)}",
                                                        "-f",
                                                        "- *",
                                                ]
                                        upload = await upload_rclone(Client, user_id, reply, command, userx, datam, search_command, check_data)
                                        if upload[0]:
                                                if not upload[1]:
                                                        if upload[2]:
                                                                try:
                                                                        fisize =str(get_human_size(getsize(output_vid)))
                                                                except:
                                                                        fisize = "Unknown"
                                                                text = f"✅{file_name} Successfully Uploade To Drive\n\n⛓Link: `{upload[3]}`\n\n💽Size: {fisize}\n\n{caption}"
                                                        else:
                                                                text = f"✅{file_name} Successfully Uploade To Drive\n\n❗Failed To Get Link: `{str(upload[3])}`\n\n{caption}"
                                                        await event.reply(text)
                                except Exception as e:
                                        await event.reply(f"❌Error While Uploading To Drive\n\n{str(e)}")
                                q+=1
                        return


async def upload_files(user_id, userx, event, final_files, caption, reply, datam, check_data, thumbnail):
    r_config = f'./userdata/{str(userx)}_rclone.conf'
    check_config = exists(r_config)
    drive_name = USER_DATA()[userx]['drive_name']
    drive_uplaod = False
    if (check_config and drive_name):
        drive_uplaod = True
    if USER_DATA()[userx]['upload_tg']:
        size = await check_size_limit()
        if (await files_size_check(final_files, size)):
            if (await files_size_check(final_files, 2097151000)):
                await upload_tg_video(Client, user_id, userx,  event, final_files, caption, reply, datam, check_data, thumbnail)
            else:
                reply = await USER.send_message(user_id, "🔼Uploading File")
                await upload_tg_video(USER, user_id, userx,  event, final_files, caption, reply, datam, check_data, thumbnail)
                await reply.delete()
        else:
            if drive_uplaod and USER_DATA()[userx]['auto_drive']:
                await upload_drive(event, user_id, reply, caption, userx, r_config, final_files, datam, check_data)
            else:
                await event.reply(f"❌File Size Is Greater Than Telegram Upload Limit")
    elif drive_uplaod:
        await upload_drive(event, user_id, reply, caption, userx, r_config, final_files, datam, check_data)
    return

async def clean_up(process_id, sub_process_id, trash_list):
    if not sub_process_id:
            remove_master_process(process_id)
    else:
        remove_sub_process(sub_process_id)
    await clear_trash_list(trash_list)
    return


async def start_process(new_event, user_id, userx, check, queue_task, url_download, ext, process_type, queue_data, pindex, process_id, check_data, trash_list):
            if not process_id:
                process_id = str(''.join(choices(ascii_lowercase + digits, k=10)))
                sub_process_id = False
            else:
                sub_process_id = str(''.join(choices(ascii_lowercase + digits, k=10)))
            if not queue_data:
                fresult = await get_filename(new_event, user_id, userx, process_id, ext, get_details(process_type, userx, True), 120, 'dw', check, url_download)
                if fresult:
                    file_loc, file_name, ext = fresult
                    trash_list.append(file_loc)
                else:
                    return
                thumbnail = await get_thumbnail(new_event, user_id, userx, 'dw',  file_name, get_details(process_type, userx, True), [f"/{process_type}", "pass"], 120)
                if thumbnail:
                    if thumbnail!='./thumb.jpg':
                        trash_list.append(thumbnail)
                else:
                    thumbnail = './thumb.jpg'
                if queue_task:
                            await add_queue(process_type, userx, new_event, url_download, file_loc, file_name, ext, thumbnail)
                            await new_event.reply("✅Task Added To Queue.")
                            return
            else:
                file_loc = queue_data[' file_loc']
                file_name = queue_data['file_name']
                ext = queue_data['ext']
                thumbnail = queue_data['thumbnail']
                url_download = queue_data['url_download']
                new_event = queue_data['event']
                process_type = queue_data['process']
                trash_list.append(file_loc)
                if thumbnail!='./thumb.jpg':
                        trash_list.append(thumbnail)
            if not sub_process_id:
                append_master_process(process_id)
                check_data = [[process_id, get_master_process()]]
                cancel_text = f"🔴Cancel Task: `/cancel mp {str(process_id)}`"
            else:
                append_sub_process(sub_process_id)
                check_data.append([sub_process_id, get_sub_process()])
                cancel_text = f"🟡Skip File: `/cancel sp {str(sub_process_id)}`\n🔴Cancel Task: `/cancel mp {str(process_id)}`"
            reply = await new_event.reply("🔽Starting Download")
            datam = [file_name, "🔽Downloading", "𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝚎𝚍", cancel_text, process_type, pindex]
            if not url_download:
                dresult = await download_tg_file(new_event, file_loc, reply, datam, check_data, userx)
            else:
                async with ClientSession() as session:
                    dresult = await download_coroutine(session, url_download, userx, file_loc, reply, check_data, datam, 3)
            if not dresult:
                await clean_up(process_id, sub_process_id, trash_list)
                return
            work_loc = await make_direc(f'{str(userx)}_work')
            progress = f"{work_loc}/progress_{file_name}.txt"
            caption = ""
            amap_options, caption = await select_audio(new_event, userx, file_loc, caption)
            file_loc, file_name, ext, caption = await change_metadata(new_event, userx, file_loc, file_name, ext, caption)
            if file_loc not in trash_list:
                trash_list.append(file_loc)
            output_file = f"{work_loc}/{file_name}"
            trash_list.append(output_file)
            duration = get_video_duration(file_loc)
            datam = [file_name, get_time(), cancel_text, process_type, pindex]
            if process_type=="compress":
                result = await Processor.compress(Client, reply, user_id, userx, file_loc, progress, amap_options, output_file, duration, check_data, datam)
            if not result:
                await clean_up(process_id, sub_process_id, trash_list)
                return
            final_files = [output_file]
            if getsize(output_file)>2097151000:
                if USER_DATA()[userx]['split_video']:
                    split_size = await get_split_size(userx)
                    if split_size:
                        datam = [file_name, get_time(), cancel_text, "split", pindex]
                        sresult = await Processor.split_video_file(Client, new_event, user_id, userx, reply, split_size, work_loc, output_file, file_name, progress, duration, datam, check_data, ext)
                        if not sresult:
                            if not (await process_checker(check_data)):
                                    await clean_up(process_id, sub_process_id, trash_list)
                                    return
                        else:
                            trash_list = trash_list + sresult
                            final_files = sresult
            datam = [file_name, '🔼Uploading Video', '𝚄𝚙𝚕𝚘𝚊𝚍𝚎𝚍', cancel_text, process_type, pindex]
            await upload_files(user_id, userx, new_event, final_files, caption, reply, datam, check_data, thumbnail)
            await send_ss(new_event, user_id, userx, duration, final_files[-1], file_name, work_loc)
            await clean_up(process_id, sub_process_id, trash_list)
            await reply.delete()
            return


################Start####################
@Client.on(events.NewMessage(incoming=True, pattern='/start'))
async def _batch(event):
    text = f"Hi {get_mention(event)}, I Am Alive."
    await event.reply(text, buttons=[
    [Button.url('⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐', 'https://t.me/nik66')],
    [Button.url('❤ Join Channel ❤', 'https://t.me/nik66x')]
])
    return


################Time####################
@Client.on(events.NewMessage(incoming=True, pattern='/time'))
async def _timecmd(event):
    user_id = event.message.chat.id
    userx = event.message.sender.id
    if userx in sudo_users:
        await event.reply(f'♻Bot Is Alive For {getbotuptime()}')
    else:
        await event.reply(f"❌Only Authorized Users Can Use This Command")
    return



################Cancel Process###########
@Client.on(events.NewMessage(incoming=True, pattern='/cancel'))
async def _cancel(event):
  user_id = event.message.chat.id
  userx = event.message.sender.id
  if userx in sudo_users:
        commands = event.message.message.split(' ')
        if len(commands)==3:
                processx = commands[1]
                process_id = commands[2]
                try:
                        if processx=='sp':
                                        dresult = remove_sub_process(process_id)
                                        if dresult:
                                            await event.reply(f'✅Successfully Cancelled.')
                                        else:
                                            await event.reply(f'❗No Running Processs With This ID')
                        elif processx=='mp':
                                        dresult =remove_master_process(process_id)
                                        if dresult:
                                            await event.reply(f'✅Successfully Cancelled.')
                                        else:
                                            await event.reply(f'❗No Running Processs With This ID')
                except Exception as e:
                        await event.reply(str(e))
                return
        else:
                await event.reply(f'❗Give Me Process ID To Cancel.')
  else:
        await event.reply(f"❌Only Authorized Users Can Use This Command")
        return


@Client.on(events.NewMessage(incoming=True, pattern='/settings'))
async def _settings(event):
        userx = event.message.sender.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        text = f"⚙ Hi {get_mention(event)} Choose Your Settings"
        await event.reply(text, buttons=[
        [Button.inline('#️⃣ General', 'general_settings')],
        [Button.inline('📝 Progress Bar', 'progress_settings')],
        [Button.inline('🏮 Compression', 'compression_settings')],
        [Button.inline('⭕Close Settings', 'close_settings')]
    ])
        return


################Download_Test####################
@Client.on(events.NewMessage(incoming=True, pattern='/compress'))
async def _compress(event):
    user_id = event.message.chat.id
    userx = event.message.sender.id
    validate = await init_user(event, userx)
    if not validate:
        return
    ext = await get_ext(event)
    queue_task = queue[userx]['started']
    new_event = await ask_media(event, user_id, userx, get_details("compress", userx, True), ["/compress", "stop"], "Send Video or URL", 120, "video/", queue_task)
    if new_event and new_event not in ["cancelled"]:
            url = await get_url_from_message(new_event)
            trash_list = []
            await start_process(new_event, user_id, userx, False, queue_task, url, ext, 'compress', False, "1/1", False, False, trash_list)
            await clear_trash_list(trash_list)
            if not queue_task:
                await asynciosleep(1)
                await event.reply("✅Task Completed Successfully")
            return


################Queue####################
@Client.on(events.NewMessage(incoming=True, pattern='/queue'))
async def _queue(event):
    user_id = event.message.chat.id
    userx = event.message.sender.id
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    if not queue[userx]['started']:
        queue[userx]['started'] = True
        await event.reply("✅Queuing Has Started, Now You Can Add Task To Queue.")
        return
    else:
        total_queue = len(queue[userx]['tasks'])
        if total_queue:
            tasks = queue[userx]['tasks']
            queue[userx]['started'] = False
            queue[userx]['tasks'] = []
            p = 1
            process_id = str(''.join(choices(ascii_lowercase + digits, k=10)))
            append_master_process(process_id)
            for queue_data in tasks:
                trash_list = []
                try:
                    await start_process(None, user_id, userx, None, False, None, None, None, queue_data, f"{str(p)}/{str(total_queue)}", process_id, [[process_id, get_master_process()]], trash_list)
                except Exception as e:
                    print(e)
                    LOGGER.info(str(e))
                await clear_trash_list(trash_list)
                if not (await process_checker([[process_id, get_master_process()]])):
                    break
                p+=1
            await event.reply("✅Task Completed Successfully")
            return
        else:
            await event.reply("❗Queue Tasks Is Empty.")
            return


################Queue####################
@Client.on(events.NewMessage(incoming=True, pattern='/clearqueue'))
async def _clearqueue(event):
    userx = event.message.sender.id
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    if not queue[userx]['started']:
        await event.reply("❗Queuing Is Not Started Yet.")
        return
    else:
        queue[userx]['tasks'] = []
        await event.reply("✅Successfully Cleared Queued Tasks")
        return


################Queue####################
@Client.on(events.NewMessage(incoming=True, pattern='/terminatequeue'))
async def _terminatequeue(event):
    userx = event.message.sender.id
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    if not queue[userx]['started']:
        await event.reply("❗Queuing Is Not Started Yet.")
        return
    else:
        queue[userx]['started'] = False
        queue[userx]['tasks'] = []
        await event.reply("✅Successfully Terminated Queuing.")
        return


################Clear One Queue####################
@Client.on(events.NewMessage(incoming=True, pattern='/clearonequeue'))
async def _clearonequeue(event):
    user_id = event.message.chat.id
    userx = event.message.sender.id
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    if not queue[userx]['started']:
        await event.reply("❗Queuing Is Not Started Yet.")
        return
    else:
        total_queue = len(queue[userx]['tasks'])
        if total_queue:
            q = 1
            msg = f"🔶Queued Tasks : {str(total_queue)}\n\n*️⃣ Send Task Index\n"
            for queue_data in queue[userx]['tasks']:
                msg+= f"`{str(q)}` - {str(queue_data['file_name'])}\n"
                q+=1
            async with Client.conversation(user_id) as conv:
                handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: int(e.message.message)), timeout=60)
                ask = await event.reply(f'{str(msg)}')
                try:
                    new_event = await handle
                except Exception as e:
                    await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                    print(e)
                    return
                try:
                    index = int(new_event.message.message)-1
                    del queue[userx]['tasks'][index]
                    q = 1
                    msg = ''
                    for queue_data in queue[userx]['tasks']:
                        msg+= f"`{str(q)}` - {str(queue_data['file_name'])}\n"
                        q+=1
                    await new_event.reply(f"✅Successfully Cleared Task\n\n🔶Queued Tasks : {str(len(queue[userx]['tasks']))}\n\n{str(msg)}")
                except Exception as e:
                    await new_event.reply(f"❗{str(e)}")
                return
        else:
            await event.reply("❗Queue Tasks Is Empty.")
            return



################Get Queue####################
@Client.on(events.NewMessage(incoming=True, pattern='/getqueue'))
async def _getqueue(event):
    user_id = event.message.chat.id
    userx = event.message.sender.id
    if userx not in sudo_users:
                    await event.reply("❌Not Authorized")
                    return
    if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
    if userx not in queue:
        queue[userx] = {}
        queue[userx]['tasks'] = []
        queue[userx]['started'] = False
    if not queue[userx]['started']:
        await event.reply("❗Queuing Is Not Started Yet.")
        return
    else:
        total_queue = len(queue[userx]['tasks'])
        if total_queue:
            q = 1
            msg = f"🔶Queued Tasks : {str(total_queue)}\n\n"
            for queue_data in queue[userx]['tasks']:
                msg+= f"`{str(q)}` - {str(queue_data['file_name'])}\n"
                q+=1
            await event.reply(msg)
            return
        else:
            await event.reply("❗Queue Tasks Is Empty.")
            return
        
############Save Rclone#############
@Client.on(events.NewMessage(incoming=True, pattern='/saveconfig'))
async def _saverclone(event):
        userx = event.message.sender.id
        user_id = event.message.chat.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        r_config = f'./userdata/{str(userx)}_rclone.conf'
        check_config = exists(r_config)
        if check_config:
                text = f"Rclone Config Already Present\n\nSend Me New Config To Replace."
        else:
                text = f"Rclone Config Not Present\n\nSend Me Config To Save."
        new_event = await ask_media(event, user_id, userx, False, ["/saveconfig", "stop"], text, 60, "text/", False)
        if new_event and new_event not in ["cancelled"]:
            await Client.download_media(new_event.message, r_config)
            accounts = await get_config(r_config)
            if not accounts:
                await delete_trash(r_config)
                await new_event.reply("❌Invalid Config File Or Empty Config File.")
                return
            await saveoptions(userx, 'drive_name', accounts[0])
            await new_event.reply(f"✅Config Saved Successfully\n\n🔶Using {str(USER_DATA()[userx]['drive_name'])} Drive For Uploading.")
        return


############Renew#############
@Client.on(events.NewMessage(incoming=True, pattern='/renew'))
async def _renew(event):
        userx = event.message.sender.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        await event.reply("*️⃣Are you sure?\n\n🚫 This will delete all your downloads and saved watermark locally 🚫", buttons=[
                [Button.inline('Yes 🚫', 'renew_True')],
                [Button.inline('No 😓', 'renew_False')]
            ])
        return
        
############Restart################
@Client.on(events.NewMessage(incoming=True, pattern='/restart'))
async def _restart(event):
        userx = event.message.sender.id
        user_id = event.message.chat.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        reply = await event.reply("♻Restarting...")
        if SAVE_TO_DATABASE:
            await save_restart(user_id, reply.id)
        execl(executable, executable, *argv)


############Add SUDO################
@Client.on(events.NewMessage(incoming=True, pattern='/addsudo'))
async def _addsudo(event):
        userx = event.message.sender.id
        user_id = event.message.chat.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        async with Client.conversation(user_id) as conv:
                handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: int(e.message.message)), timeout=60)
                ask = await event.reply(f'*️⃣Send User Numerical ID')
                try:
                    new_event = await handle
                except Exception as e:
                    await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                    print(e)
                    return
        ask_id = int(new_event.message.message)
        if ask_id not in sudo_users:
            sudo_users.append(ask_id)
            await new_event.reply(f"✅Successfully Added User To Sudo Users\n\n{str(sudo_users)}")
        else:
            await new_event.reply(f"❗User Already In Sudo Users\n\n{str(sudo_users)}")
        return



############DeleteSUDO################
@Client.on(events.NewMessage(incoming=True, pattern='/delsudo'))
async def _delsudo(event):
        userx = event.message.sender.id
        user_id = event.message.chat.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        async with Client.conversation(user_id) as conv:
                handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: int(e.message.message)), timeout=60)
                ask = await event.reply(f'*️⃣Send User Numerical ID')
                try:
                    new_event = await handle
                except Exception as e:
                    await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                    print(e)
                    return
        ask_id = int(new_event.message.message)
        if ask_id in sudo_users:
            sudo_users.remove(ask_id)
            await new_event.reply(f"✅Successfully Removed User From Sudo Users\n\n{str(sudo_users)}")
        else:
            await new_event.reply(f"❗User Not In Sudo Users\n\n{str(sudo_users)}")
        return
    

############GetSUDO################
@Client.on(events.NewMessage(incoming=True, pattern='/getsudo'))
async def _getsudo(event):
        userx = event.message.sender.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        await event.reply(f"{str(sudo_users)}")
        return
    

############Get Logs Message################
@Client.on(events.NewMessage(incoming=True, pattern='/log'))
async def _log(event):
        userx = event.message.sender.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
                await event.reply(str(get_logs_msg(log_file)))
        else:
            await event.reply("❗Log File Is Not Found")
        return


############Get Log File################
@Client.on(events.NewMessage(incoming=True, pattern='/logs'))
async def _logs(event):
        userx = event.message.sender.id
        user_id = event.message.chat.id
        if userx not in sudo_users:
                        await event.reply("❌Not Authorized")
                        return
        if userx not in USER_DATA():
                await new_user(userx, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
            await Client.send_file(user_id, file=log_file, allow_cache=False)
        else:
            await event.reply("❗Log File Is Not Found")
        return