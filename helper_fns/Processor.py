from config import Config
from telethon import events
from time import time
from helper_fns.Helper import get_readable_time, USER_DATA, get_video_duration, get_details, Timer, make_direc, clear_trash_list, process_checker, get_time, execute, delete_trash, get_human_size, gen_random_string
from helper_fns.Ruunung_Process import append_master_process, remove_master_process, get_master_process, append_sub_process, remove_sub_process, get_sub_process
from helper_fns.Progress_Bar import progress_bar
from helper_fns.Video_Engine import Processor
from json import loads
from helper_fns.FFMPEG_Engine import run_process_command
from os.path import getsize, exists
from os import remove
from re import escape, findall
from helper_fns.FFMPEG_Engine import upload_rclone
from aiohttp import ClientSession
from asyncio import sleep as asynciosleep
from aiofiles import open as aiofiles_open
from helper_fns.Telethon_FNs import download_tg_file, upload_tg_video
from helper_fns.Queue import get_queue


#////////////////////////////////////Variables////////////////////////////////////#
USER = Config.USER
LOGGER = Config.LOGGER
punc = ['!', '|', '{', '}', ';', ':', "'", '=', '"', '\\', ',', '<', '>', '/', '?', '@', '#', '$', '%', '^', '&', '*', '~', "  ", "\t", "+", "b'", "'"]


#////////////////////////////////////Functions////////////////////////////////////#
async def add_queue(process, userx, new_event, url_download, file_loc, file_name, ext, thumbnail, *merge_list):
    queue_data = {}
    queue_data['event'] = new_event
    queue_data['url_download'] = url_download
    queue_data['process'] = process
    queue_data[' file_loc'] =  file_loc
    queue_data['file_name'] = file_name
    queue_data['ext'] = ext
    queue_data['thumbnail'] = thumbnail
    if process=="merge":
        queue_data['merge_list'] = merge_list[0]
    get_queue()[userx]['tasks'].append(queue_data)
    return


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


async def clean_up(process_id, sub_process_id, trash_list):
    if not sub_process_id:
            remove_master_process(process_id)
    else:
        remove_sub_process(sub_process_id)
    await clear_trash_list(trash_list)
    return


#////////////////////////////////////Processor////////////////////////////////////#

###############------Start_Processing------###############
async def start_process(tgclient, new_event, user_id, userx, check, queue_task, url_download, ext, process_type, queue_data, pindex, process_id, check_data, trash_list, *merge_list):
            if not process_id:
                process_id = gen_random_string(10)
                sub_process_id = False
            else:
                sub_process_id = gen_random_string(10)
            if not queue_data:
                fresult = await get_filename(tgclient, new_event, user_id, userx, process_id, ext, get_details(process_type, userx, True), 120, 'dw', check, url_download)
                if fresult:
                    file_loc, file_name, ext = fresult
                    trash_list.append(file_loc)
                else:
                    return
                thumbnail = await get_thumbnail(tgclient, new_event, user_id, userx, 'dw',  file_name, get_details(process_type, userx, True), [f"/{process_type}", "pass"], 120)
                if thumbnail:
                    if thumbnail!='./thumb.jpg':
                        trash_list.append(thumbnail)
                else:
                    thumbnail = './thumb.jpg'
                if queue_task:
                            await add_queue(process_type, userx, new_event, url_download, file_loc, file_name, ext, thumbnail, *merge_list)
                            await new_event.reply("✅Task Added To Queue.")
                            return
                if process_type=="merge":
                    merge_list = merge_list[0]
                    dw_files = len(merge_list)
                else:
                    merge_list = []
                    dw_files = 1
            else:
                file_loc, file_name, ext, thumbnail, url_download, new_event, process_type, merge_list, dw_files = await get_queue_data(queue_data)
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
            infile_names = ''
            reply = False
            for i in range(dw_files):
                    if process_type=="merge":
                            url_download = merge_list[i][0]
                            dw_event = merge_list[i][1]
                            dwfile_loc, dwfile_name, dwext = merge_list[i][2]
                    else:
                            dw_event = new_event
                            dwfile_loc, dwfile_name, dwext = file_loc, file_name, ext
                    trash_list.append(dwfile_loc)
                    if reply:
                        await reply.delete()
                        await asynciosleep(4)
                    reply = await dw_event.reply("🔽Starting Download")
                    datam = [dwfile_name, f"🔽Downloading [{str(i+1)}/{str(dw_files)}]", "𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝚎𝚍", cancel_text, process_type, pindex]
                    if not url_download:
                        dresult = await download_tg_file(tgclient, dw_event, dwfile_loc, reply, datam, check_data, userx)
                    else:
                        async with ClientSession() as session:
                            dresult = await download_coroutine(session, url_download, userx, dwfile_loc, reply, check_data, datam, 3)
                    if not dresult:
                        await clean_up(process_id, sub_process_id, trash_list)
                        return
                    infile_names += f"file '{str(dwfile_loc)}'\n"
            if process_type=="merge":
                    duration = 0
                    await reply.delete()
                    await asynciosleep(2)
                    reply = await new_event.reply("⚙ Processing")
            else:
                    duration = get_video_duration(file_loc)
            work_loc = await make_direc(f'{str(userx)}_work')
            progress = f"{work_loc}/progress_{file_name}.txt"
            caption = f"⚡{str(process_type).upper()}⚡\n\n"
            if process_type!="merge":
                    amap_options, caption = await select_audio(new_event, userx, file_loc, caption)
                    file_loc, file_name, ext, caption = await change_metadata(new_event, userx, file_loc, file_name, ext, caption)
                    if file_loc not in trash_list:
                        trash_list.append(file_loc)
            output_file = f"{work_loc}/{file_name}"
            trash_list.append(output_file)
            datam = [file_name, get_time(), cancel_text, process_type, pindex]
            if process_type=="compress":
                result = await Processor.compress(tgclient, reply, user_id, userx, file_loc, progress, amap_options, output_file, duration, check_data, datam)
            elif process_type=="merge":
                concat_file = f"{str(file_name)}_{str(userx)}_merge_concat.txt"
                trash_list.append(concat_file)
                with open(concat_file, 'w', encoding="utf-8") as f:
                        f.write(str(infile_names.strip()))
                result = await Processor.merge(tgclient, reply, user_id, userx, concat_file, progress, output_file, duration, check_data, datam, dw_files)
            elif process_type=="watermark":
                result = await Processor.watermark(tgclient, reply, user_id, userx, file_loc, progress, amap_options, output_file, duration, check_data, datam)
            if not result:
                await clean_up(process_id, sub_process_id, trash_list)
                return
            if process_type=="merge":
                    amap_options, caption = await select_audio(new_event, userx, output_file, caption)
                    output_file, file_name, ext, caption = await change_metadata(new_event, userx, output_file, file_name, ext, caption)
                    if output_file not in trash_list:
                        trash_list.append(output_file)
            duration = get_video_duration(output_file)
            final_files = [output_file]
            if getsize(output_file)>2097151000:
                if USER_DATA()[userx]['split_video']:
                    split_size = await get_split_size(userx)
                    if split_size:
                        datam = [file_name, get_time(), cancel_text, "split", pindex]
                        sresult = await Processor.split_video_file(tgclient, new_event, user_id, userx, reply, split_size, work_loc, output_file, file_name, progress, duration, datam, check_data, ext)
                        if not sresult:
                            if not (await process_checker(check_data)):
                                    await clean_up(process_id, sub_process_id, trash_list)
                                    return
                        else:
                            trash_list = trash_list + sresult
                            final_files = sresult
            datam = [file_name, '🔼Uploading Video', '𝚄𝚙𝚕𝚘𝚊𝚍𝚎𝚍', cancel_text, process_type, pindex]
            await upload_files(tgclient, user_id, userx, new_event, final_files, caption, reply, datam, check_data, thumbnail)
            await send_sample_video(tgclient, new_event, user_id, userx, duration, final_files[-1], file_name, work_loc)
            await send_ss(tgclient, new_event, user_id, userx, duration, final_files[-1], file_name, work_loc, False)
            await clean_up(process_id, sub_process_id, trash_list)
            await reply.delete()
            return
        
###############------Get_Queue_Data------###############
async def get_queue_data(queue_data):
    file_loc = queue_data[' file_loc']
    file_name = queue_data['file_name']
    ext = queue_data['ext']
    thumbnail = queue_data['thumbnail']
    url_download = queue_data['url_download']
    new_event = queue_data['event']
    process_type = queue_data['process']
    if process_type=="merge":
        merge_list = queue_data["merge_list"]
        dw_files = len(merge_list)
    else:
        merge_list = False
        dw_files = 1
    return [file_loc, file_name, ext, thumbnail, url_download, new_event, process_type, merge_list, dw_files]


###############------Send_Sample_Video------###############
async def send_sample_video(tgclient, event, user_id, userx, duration, input_video, file_name, work_loc):
    if duration>60:
        if USER_DATA()[userx]['gen_sample']:
                sample_name = f"{work_loc}/sample_{file_name}"
                vstart_time, vend_time = await get_cut_duration(duration)
                cmd_sample = ["ffmpeg", "-ss", str(vstart_time), "-to",  str(vend_time), "-i", f"{input_video}","-c", "copy", '-y', f"{sample_name}"]
                sample_result = await run_process_command(cmd_sample)
                if sample_result and exists(sample_name):
                    sscaption = f"🎞 Sample Video"
                    try:
                        await tgclient.send_file(user_id, file=sample_name, allow_cache=False, reply_to=event.message, caption=sscaption)
                    except:
                        pass
                    remove(sample_name)
    return



###############------Get_Sample_Video_Cut_Duration------###############
async def get_cut_duration(duration):
    if duration<60:
                return [1, duration-2]
    else:
        vmid = round(duration/2)-2
        vend = vmid+60
        if vend>duration:
            vend = duration-2
        return [vmid, vend]


###############------Select_Audio------###############
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


###############------Change_Metadata------###############
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
    

###############------Get_Thumbnail------###############
async def get_thumbnail(tgclient, event, user_id, userx, loc,  filename, detailed_message, keywords, timeout):
    thumb = './thumb.jpg'
    if USER_DATA()[userx]['custom_thumbnail']:
        async with tgclient.conversation(user_id) as conv:
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
            await tgclient.download_media(new_event.message, custom_thumb)
            return custom_thumb
    else:
        return thumb


###############------Get_FileName------###############
async def get_filename(tgclient, event, user_id, userx, process_id, ext, detailed_message, timeout, loc, check, url):
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
        async with tgclient.conversation(user_id) as conv:
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
        async with tgclient.conversation(user_id) as conv:
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


#////////////////////////////////////Uploader////////////////////////////////////#

###############------Uploade_Files------###############
async def upload_files(tgclient, user_id, userx, event, final_files, caption, reply, datam, check_data, thumbnail):
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
                await upload_tg_video(tgclient, user_id, userx,  event, final_files, caption, reply, datam, check_data, thumbnail)
            else:
                reply = await USER.send_message(user_id, "🔼Uploading File")
                await upload_tg_video(USER, user_id, userx,  event, final_files, caption, reply, datam, check_data, thumbnail)
                await reply.delete()
        else:
            if drive_uplaod and USER_DATA()[userx]['auto_drive']:
                await upload_drive(tgclient, event, user_id, reply, caption, userx, r_config, final_files, datam, check_data)
            else:
                await event.reply(f"❌File Size Is Greater Than Telegram Upload Limit")
    elif drive_uplaod:
        await upload_drive(tgclient, event, user_id, reply, caption, userx, r_config, final_files, datam, check_data)
    return


#////////////////////////////////////ScreenShoot_Generator////////////////////////////////////#

###############------Generate_ScreenShot------###############
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


###############------Get_ScreenShot_List------###############
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


###############------Send_ScreenShots------###############
async def send_ss(tgclient, event, user_id, userx, duration, input_video, file_name, work_loc, check_no):
    if USER_DATA()[userx]['gen_ss'] or check_no:
        if not check_no:
            ss_n0 = USER_DATA()[userx]['ss_no']
        else:
            ss_n0 = check_no
        ss_list = await gen_ss_list(duration, ss_n0)
        sn0 = 1
        for ss_time in ss_list:
            ss_name = f"{work_loc}/{file_name}_{str(time())}.jpg"
            ssresult = await generate_screenshoot(ss_time, input_video, ss_name)
            if ssresult and exists(ss_name):
                sscaption = f"📌 Position: {str(get_readable_time(ss_time))}\n📷 Screenshot: {str(sn0)}/{str(ss_n0)}"
                try:
                    await tgclient.send_file(user_id, file=ss_name, allow_cache=False, reply_to=event.message, caption=sscaption)
                except:
                    pass
                remove(ss_name)
                sn0+=1
                await asynciosleep(1)
    return


#////////////////////////////////////AioHTTO////////////////////////////////////#

###############------Download_From_URL------###############
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


#////////////////////////////////////Rclone////////////////////////////////////#

###############------Upload_To_Drive------###############
async def upload_drive(tgclient, event, user_id, reply, caption, userx, r_config, final_files, datam, check_data):
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
                                        upload = await upload_rclone(tgclient, user_id, reply, command, userx, datam, search_command, check_data)
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
