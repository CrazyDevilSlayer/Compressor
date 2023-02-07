from config import Config
from time import time
from helper_fns.Helper import USER_DATA,get_video_duration,Timer
from telethon.tl.types import DocumentAttributeVideo
from helper_fns.Fast_Telethon import upload_file, download_file
from helper_fns.Progress_Bar import progress_bar
# from hachoir.metadata import extractMetadata
# from hachoir.parser import createParser


#////////////////////////////////////Variables////////////////////////////////////#
LOGGER = Config.LOGGER


#////////////////////////////////////Telethon_Functions////////////////////////////////////#


###############------Download_Telegram_File------###############
async def download_tg_file(Client, new_event, download_location, reply, datam, check_data, userx):
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
                        await reply.edit("🔒Task Cancelled By User")
                else:
                    await reply.edit(str(e))
                    LOGGER.info(str(e))
                return False
        return True


###############------Upload_Telegram_File------###############
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
                caption = f"🔷{filename}\n" + str(caption).strip()
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

