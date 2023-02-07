from math import floor as mathfloor
from re import findall as refindall
from asyncio import create_subprocess_exec, create_task, FIRST_COMPLETED
from asyncio import wait as asynciowait
from asyncio.subprocess import PIPE as asyncioPIPE
from helper_fns.Helper import getbotuptime, get_readable_time, delete_trash, get_human_size, get_stats, get_time, process_checker, Timer, USER_DATA, get_details, check_files_exists, create_process_file, get_current_time
from asyncio import sleep as assleep
from helper_fns.Progress_Bar import get_progress_bar_string, get_progress_bar_from_percentage
from os.path import getsize
from json import loads
from telethon.errors import FloodWaitError
from config import Config


#////////////////////////////////////Variables////////////////////////////////////#
all_data = []
msg_data = ['Processing']
running_process = []
wpositions = {'5:5': 'Top Left', 'main_w-overlay_w-5:5': 'Top Right', '5:main_h-overlay_h': 'Bottom Left', 'main_w-overlay_w-5:main_h-overlay_h-5': 'Bottom Right'}
LOGGER = Config.LOGGER


#////////////////////////////////////Functions////////////////////////////////////#

###############------Task_Checker------###############
async def check_task(check_data):
    while True:
        await assleep(1)
        checker = await process_checker(check_data)
        if not checker:
            break
    return

###############------Logger------###############
async def get_logs(process, check_data):
        while True:
                    try:
                            async for line in process:
                                        line = line.decode('utf-8').strip()
                                        print(line)
                                        all_data.append(line)
                                        if len(line)<3800:
                                            msg_data[-1] = line
                                        checker = await process_checker(check_data)
                                        if not checker:
                                            break
                    except ValueError:
                            continue
                    else:
                            break
        return

###############------Cleaner------###############
async def clear_tasks(task, pending, process, update_msg, log_task):
    if task not in pending:
                try:
                        print("🔶Terminating Process")
                        process.terminate()
                except Exception as e:
                        print(e)
    else:
                try:
                        print("🔶Cancelling Task")
                        task.cancelled()
                        await task
                except Exception as e:
                        print(e)
    try:
            print("🔶Cancelling Updater")
            update_msg.cancelled()
            await update_msg
    except Exception as e:
            print(e)
    if log_task:
        try:
                print("🔶Cancelling Logger")
                log_task.cancelled()
                await log_task
        except Exception as e:
                print(e)
    return


#////////////////////////////////////FFMPEG_Functions////////////////////////////////////#

###############------FFMPEG_Engine------###############
async def ffmpeg_engine(Client, user_id, userx, reply, command, input_file, output_file, progress, duration, check_data, datam, show_progress):
    global all_data
    global msg_data
    print(command)
    await create_process_file(progress)
    await delete_trash(output_file)
    all_data = []
    msg_data = ['Processing']
    process_start_time = get_time()
    process = await create_subprocess_exec(
            *command,
            stdout=asyncioPIPE,
            stderr=asyncioPIPE,
            )
    pid = process.pid
    running_process.append(pid)
    check_data.append([pid, running_process])
    task = create_task(check_task(check_data))
    log_task = create_task(get_logs(process.stderr, check_data))
    update_msg = create_task(update_message(reply, userx, input_file, output_file, progress, duration, process_start_time, check_data, datam, show_progress))
    done, pending = await asynciowait([task, process.wait()], return_when=FIRST_COMPLETED)
    return_code = process.returncode
    running_process.remove(pid)
    await delete_trash(progress)
    await clear_tasks(task, pending, process, update_msg, log_task)
    del check_data[-1]
    checker = await process_checker(check_data)
    if not checker:
        all_data = []
        msg_data = ['Processing']
        return [True, True]
    elif return_code == 0:
        all_data = []
        msg_data = ['Processing']
        return [True, False]
    else:
        try:
            failed_ext = str(output_file).split("/")[-1].split(".")[-1]
        except:
            failed_ext = "Unknown"
        cc=f"{str(datam[0])}\n\n❌{str(datam[3]).upper()} Process Failed\nFile Ext: {str(failed_ext)}\n\n🔶Return Code: {str(return_code)}"
        fail_file = f"{str(datam[0])}_{str(datam[3]).upper()}_log.txt"
        with open(fail_file, 'w', encoding="utf-8") as f:
                f.write(str(all_data))
        await Client.send_file(user_id, file=fail_file, allow_cache=False, caption=cc)
        all_data = []
        msg_data = ['Processing']
        await delete_trash(fail_file)
        await reply.edit(cc)
        return [False]

###############------Get_Values_FFMPEG------###############
def get_value(dlist, dtype, value):
    if len(dlist):
        try:
            return dtype(dlist[-1].strip())
        except:
            return value
    else:
        return value

###############------FFMPEG_Progress_Updater------###############
async def update_message(reply, userx, input_file, output_file, process_log, duration, process_start_time, check_data, datam, show_progress):
            if show_progress:
                txt = ''
                mas_time = datam[1]
                process_head1 = f"{str(datam[5])}\n🎟️File: {datam[0]}"
                process_head2 = f"🧭Duration: {get_readable_time(duration)}\n💽IN Size: {str(get_human_size(getsize(input_file)))}"
                while True:
                    checker = await process_checker(check_data)
                    if not checker:
                            break
                    if (await check_files_exists([output_file, process_log])):
                        print("🔶Process Has Started")
                        break
                    else:
                        print("🔶Waiting For Process To Start")
                    await assleep(1)
                while True:
                        checker = await process_checker(check_data)
                        if not checker:
                            break
                        current_time = get_time()
                        detailed_message = get_details(datam[3], userx, False)
                        if detailed_message:
                            process_head = process_head1 + "\n" + detailed_message + "\n" +process_head2 + f"\n🛠Task: {str(datam[4])}"
                        else:
                            process_head = process_head1 + f"\n🛠Task: {str(datam[4])}"
                        progress_mid = ''
                        process_foot = ''
                        ffmpeg_log = ""
                        if USER_DATA()[userx]['show_time']:
                                process_foot+= "⌚Time: " + get_current_time() + "\n"
                        if USER_DATA()[userx]['show_botuptime']:
                            process_foot += f"♥️Bot Uptime: {str(getbotuptime())}\n"
                        if USER_DATA()[userx]['ffmpeg_log']:
                                try:
                                        logs = all_data[-2] + "\n" + msg_data[-1]
                                except:
                                    logs = msg_data[-1]
                                if len(logs)>3000:
                                    logs = msg_data[-1]
                                ffmpeg_log+= f"⚡️●●●● 𝙿𝚛𝚘𝚌𝚎𝚜𝚜 ●●●●⚡️\n\n⚙{str(logs)}\n\n\n"
                        if USER_DATA()[userx]['ffmpeg_size']:
                            ot_size = getsize(output_file)
                            progress_mid+= f"💾OT Size: {str(get_human_size(ot_size))}\n"
                        if USER_DATA()[userx]['ffmpeg_ptime']:
                            progress_mid += f"🧭Elapsed Time: {str(get_readable_time(current_time - process_start_time))}\n🔹MP Time: {str(get_readable_time(current_time - mas_time))}\n"
                        with open(process_log, 'r+') as file:
                            text = file.read()
                            time_in_us = get_value(refindall("out_time_ms=(.+)", text), int, 1)
                            bitrate = get_value(refindall("bitrate=(.+)", text), str, "0")
                            fps = get_value(refindall("fps=(.+)", text), str, "0")
                            progress=get_value(refindall("progress=(\w+)", text), str, "end")
                            speed=get_value(refindall("speed=(\d+\.?\d*)", text), float, 1)
                            if progress == "end":
                                    break
                            elapsed_time = time_in_us/1000000
                            difference = mathfloor( (duration - elapsed_time) / speed)
                            ETA = "-"
                            if difference > 0:
                                ETA = get_readable_time(difference)
                            progress_mid = f"⏰️ETA Time: {ETA}\n" + progress_mid
                            if USER_DATA()[userx]['ffmpeg_size']:
                                progress_mid = f"🚂ETA Size: {str(get_human_size((ot_size/time_in_us)*duration*1024*1024))}\n" + progress_mid
                            pro_bar = f"{str(process_head)}\n\n\n{get_progress_bar_string(elapsed_time, duration)}\n\n ┌ 𝙿𝚛𝚘𝚐𝚛𝚎𝚜𝚜:【 {elapsed_time * 100 / duration:.1f}% 】\n ├ 𝚂𝚙𝚎𝚎𝚍:【 {speed}x 】\n ├ 𝙱𝚒𝚝𝚛𝚊𝚝𝚎:【 {bitrate} 】\n ├ 𝙵𝙿𝚂:【 {fps} 】\n ├ 𝚁𝚎𝚖𝚊𝚒𝚗𝚒𝚗𝚐:【 {get_readable_time((duration - elapsed_time))} 】\n └ 𝙿𝚛𝚘𝚌𝚎𝚜𝚜𝚎𝚍:【 {str(get_readable_time(elapsed_time))} 】\n\n\n{ffmpeg_log}{progress_mid}{str(get_stats(userx))}\n{str(process_foot)}{str(datam[2])}"
                        if txt!=pro_bar:
                                txt=pro_bar
                                try:
                                    await reply.edit(pro_bar)
                                except FloodWaitError as e:
                                    await assleep(e.seconds+5)
                                except Exception as e:
                                    print(e)
                        await assleep(USER_DATA()[userx]['update_time'])
            else:
                try:
                    await reply.edit(f"{str(datam[5])}\n🎟️File: {datam[0]}\n🛠Task: {str(datam[4])}")
                except Exception as e:
                    print(e)
            return
        

#////////////////////////////////////Rclone_Functions////////////////////////////////////#

###############------Rclone_Engine------###############
async def upload_rclone(Client, user_id, reply, command, userx, datam, search_command, check_data):
    global all_data
    global msg_data
    print(command)
    all_data = []
    msg_data = ['Processing']
    process_start_time = get_time()
    process = await create_subprocess_exec(
            *command,
            stdout=asyncioPIPE,
            stderr=asyncioPIPE,
            )
    pid = process.pid
    running_process.append(pid)
    check_data.append([pid, running_process])
    task = create_task(check_task(check_data))
    update_msg = create_task(update_rclone_message(process.stdout, userx, reply, datam, check_data, process_start_time))
    done, pending = await asynciowait([task, process.wait()], return_when=FIRST_COMPLETED)
    return_code = process.returncode
    running_process.remove(pid)
    await clear_tasks(task, pending, process, update_msg, False)
    del check_data[-1]
    checker = await process_checker(check_data)
    if not checker:
        all_data = []
        msg_data = ['Processing']
        return [True, True]
    elif return_code == 0:
        all_data = []
        msg_data = ['Processing']
        drive_link = await getdrivelink(search_command)
        if drive_link[0]:
            return [True, False, True, drive_link[1]]
        else:
            return [True, False, False, drive_link[1]]
    else:
        cc=f"{str(datam[0])}\n\n❌Rclone Upload Process Failed\n\n🔶Return Code: {str(return_code)}"
        fail_file = f"{str(datam[0])}_Rclone Upload_log.txt"
        with open(fail_file, 'w', encoding="utf-8") as f:
                f.write(str(all_data))
        await Client.send_file(user_id, file=fail_file, allow_cache=False, caption=cc)
        all_data = []
        msg_data = ['Processing']
        await delete_trash(fail_file)
        await reply.edit(cc)
        return [False]

###############------Rclone_Progress_Updater------###############
async def update_rclone_message(process, userx, reply, datam, check_data, process_start_time):
        timer = Timer(USER_DATA()[userx]['update_time'])
        txt = ''
        # fsize = str(get_human_size(getsize(input_vid)))
        while True:
                    try:
                            async for line in process:
                                        checker = await process_checker(check_data)
                                        if not checker:
                                            break
                                        line = line.decode().strip()
                                        print(line)
                                        all_data.append(line)
                                        if len(line)<3800:
                                            msg_data[-1] = line
                                        if timer.can_send():
                                            try:
                                                mat = refindall("Transferred:.*ETA.*", line)
                                                if mat is not None:
                                                    if len(mat) > 0:
                                                        nstr = mat[0].replace("Transferred:", "")
                                                        nstr = nstr.strip()
                                                        nstr = nstr.split(",")
                                                        prg = nstr[1].strip("% ")
                                                        progress = get_progress_bar_from_percentage(prg)
                                                        dwdata = nstr[0].strip().split('/')
                                                        cur = dwdata[0].strip()
                                                        fsize = dwdata[1].strip()
                                                        eta = nstr[3].strip().replace('ETA', '').strip()
                                                        process_head = f"{str(datam[1])}\n🎟️File: {datam[0]}"
                                                        process_foot = ""
                                                        if USER_DATA()[userx]['ffmpeg_ptime']:
                                                            process_foot += f"🧭Elapsed Time: {str(get_readable_time(get_time() - process_start_time))}\n"
                                                        process_foot += f"⏰️ETA Time: {eta}\n{str(get_stats(userx))}"
                                                        if USER_DATA()[userx]['show_time']:
                                                            process_foot+= "\n⌚Time: " + get_current_time()
                                                        if USER_DATA()[userx]['show_botuptime']:
                                                                process_foot += f"\n♥️Bot Uptime: {str(getbotuptime())}"
                                                        detailed_message = get_details(datam[4], userx, False)
                                                        if detailed_message:
                                                            process_head = process_head + "\n" + detailed_message + f"\n🛠Task: {str(datam[5])}"
                                                        else:
                                                            process_head = process_head + f"\n🛠Task: {str(datam[5])}"
                                                        pro_bar = f"{str(process_head)}\n\n\n{str(progress)}\n\n ┌ 𝙿𝚛𝚘𝚐𝚛𝚎𝚜𝚜:【 {prg}% 】\n ├ 𝚂𝚙𝚎𝚎𝚍:【 {nstr[2]} 】\n ├ {datam[2]}:【 {cur} 】\n └ 𝚂𝚒𝚣𝚎:【 {fsize} 】\n\n\n{str(process_foot)}\n{str(datam[3])}"
                                                        if txt!=pro_bar:
                                                            txt=pro_bar
                                                            try:
                                                                await reply.edit(pro_bar)
                                                            except FloodWaitError as e:
                                                                await assleep(e.seconds+5)
                                                            except Exception as e:
                                                                await reply.edit(e)
                                                                print(e)
                                                                LOGGER.info(str(e))
                                            except Exception as e:
                                                            await reply.edit(text=f'❌Error While Updating Message: {str(e)}')
                                                            LOGGER.info(str(e))
                    except ValueError:
                            continue
                    else:
                            break
        return

###############------Get_Uploaded_File_Link------###############
async def getdrivelink(search_command):
    process = await create_subprocess_exec(
        *search_command, stdout=asyncioPIPE
    )
    stdout, _ = await process.communicate()
    try:
        stdout = stdout.decode().strip()
        print(stdout)
        data = loads(stdout)
        gid = data[0]["ID"]
        # name = data[0]["Name"]
        # link = f'https://drive.google.com/file/d/{gid}/view'
        # print(link)
        return [True, gid]
    except Exception as e:
        return [False, e]


#////////////////////////////////////Other_Functions////////////////////////////////////#

###############------Run_Command------###############
async def run_process_command(command):
    print(command)
    try:
        process = await create_subprocess_exec(
            *command,
            stdout=asyncioPIPE,
            stderr=asyncioPIPE,
            )
        while True:
                    try:
                            async for line in process.stderr:
                                        line = line.decode('utf-8').strip()
                                        print(line)
                    except ValueError:
                            continue
                    else:
                            break
        await process.wait()
        return_code = process.returncode
        if return_code == 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False