from asyncio import sleep as asynciosleep
from helper_fns.Helper import hrb, get_readable_time, get_stats, USER_DATA, getbotuptime, get_details, get_current_time
from telethon.errors import FloodWaitError
from time import time


###############------Get_Progress_Bar------###############
def get_progress_bar_string(current,total):
    completed = int(current) / 8
    total = int(total) / 8
    p = 0 if total == 0 else round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 6
    p_str = '■' * cFull
    p_str += '□' * (16 - cFull)
    p_str = f"[{p_str}]"
    return p_str


###############------Get_Progress_Bar_From_Percentage------###############
def get_progress_bar_from_percentage(percentage):
    try:
        p = int(percentage)
    except:
        p = 0
    p = min(max(p, 0), 100)
    cFull = p // 6
    p_str = '■' * cFull
    p_str += '□' * (16 - cFull)
    p_str = f"[{p_str}]"
    return p_str


###############------Progress_Updater------###############
async def progress_bar(current,total,reply, start, datam, userx, timer):
      if timer.can_send():
        diff = time() - start
        if diff < 1:
            return
        else:
            speed = current / round(diff)
            progress = get_progress_bar_string(current,total)
            process_head = f"{str(datam[1])}\n🎟️File: {datam[0]}"
            process_foot = ""
            if USER_DATA()[userx]['ffmpeg_ptime']:
                process_foot += f"🧭Elapsed Time: {get_readable_time(diff)}\n"
            process_foot += f"⏰️ETA Time: {get_readable_time((total-current)/speed)}\n{str(get_stats(userx))}"
            if USER_DATA()[userx]['show_time']:
                    process_foot+= "\n⌚Time: " + get_current_time()
            if USER_DATA()[userx]['show_botuptime']:
                    process_foot += f"\n♥️Bot Uptime: {str(getbotuptime())}"
            detailed_message = get_details(datam[4], userx, False)
            if detailed_message:
                process_head = process_head + "\n" + detailed_message + f"\n🛠Task: {str(datam[5])}"
            else:
                process_head = process_head + f"\n🛠Task: {str(datam[5])}"
            pro_bar = f"{str(process_head)}\n\n\n{str(progress)}\n\n ┌ 𝙿𝚛𝚘𝚐𝚛𝚎𝚜𝚜:【 {current * 100 / total:.1f}% 】\n ├ 𝚂𝚙𝚎𝚎𝚍:【 {str(hrb(speed))}ps 】\n ├ {datam[2]}:【 {hrb(current)} 】\n └ 𝚂𝚒𝚣𝚎:【 {hrb(total)} 】\n\n\n{str(process_foot)}\n{str(datam[3])}"
            try:
                await reply.edit(pro_bar)
            except FloodWaitError as e:
                await asynciosleep(e.seconds+5)
            return