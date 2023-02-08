from telethon import events
from telethon.tl.custom import Button
from config import Config
from helper_fns.Helper import USER_DATA, saveconfig, delete_all, delete_trash,saveoptions, get_config, resetdatabase, new_user
from os import listdir
from os.path import isfile, exists




#////////////////////////////////////Variables////////////////////////////////////#
sudo_users = Config.SUDO_USERS
encoders_list = ['libx265', 'libx264']
crf_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51']
wsize_list =['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25']
presets_list =  ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
bool_list = [True, False]
ws_name = {'5:5': 'Top Left', 'main_w-overlay_w-5:5': 'Top Right', '5:main_h-overlay_h': 'Bottom Left', 'main_w-overlay_w-5:main_h-overlay_h-5': 'Bottom Right'}
ws_value = {'Top Left': '5:5', 'Top Right': 'main_w-overlay_w-5:5', 'Bottom Left': '5:main_h-overlay_h', 'Bottom Right': 'main_w-overlay_w-5:main_h-overlay_h-5'}
Client = Config.client
punc = ['!', '|', '{', '}', ';', ':', "'", '=', '"', '\\', ',', '<', '>', '/', '?', '@', '#', '$', '%', '^', '&', '*', '~', "  ", "\t", "+", "b'", "'"]
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE


#////////////////////////////////////Functions////////////////////////////////////#
def get_mention(event):
    return "["+event.sender.first_name+"](tg://user?id="+str(event.sender.id)+")"

def gen_keyboard(values_list, current_value, callvalue, items, hide):
    boards = []
    lists = len(values_list)//items
    if lists!=len(values_list)/items:
        lists +=1
    current_list = []
    for x in values_list:
        if len(current_list)==items:
            boards.append(current_list)
            current_list = []
        value = f"{str(callvalue)}_{str(x)}"
        if current_value!=x:
            if callvalue!="watermarkposition":
                text = f"{str(x)}"
            else:
                    text = f"{str(ws_name[x])}"
        else:
            if not hide:
                if callvalue!="watermarkposition":
                    text = f"{str(x)} 🟢"
                else:
                    text = f"{str(ws_name[x])} 🟢"
            else:
                text = f"🟢"
        keyboard = Button.inline(text, value)
        current_list.append(keyboard)
    boards.append(current_list)
    return boards

async def get_metadata(user_id, userx, event, timeout, message):
    async with Client.conversation(user_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=user_id, incoming=True, from_users=[userx], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'*️⃣ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                print(e)
                return False
            metadata = new_event.message.message
            for ele in punc:
                if ele in metadata:
                        metadata = metadata.replace(ele, '')
            return metadata


#////////////////////////////////////Callbacks////////////////////////////////////#
@Client.on(events.CallbackQuery)
async def callback(event):
        txt = event.data.decode()
        user_id = event.chat.id
        userx = event.sender.id
        if userx not in USER_DATA():
            await new_user(userx, SAVE_TO_DATABASE)
        
        if txt.startswith("settings"):
            text = f"⚙ Hi {get_mention(event)} Choose Your Settings"
            await event.edit(text, buttons=[
            [Button.inline('#️⃣ General', 'general_settings')],
            [Button.inline('📝 Progress Bar', 'progress_settings')],
            [Button.inline('🏮 Compression', 'compression_settings')],
            [Button.inline('🍧 Merge', 'merge_settings')],
            [Button.inline('🛺 Watermark', 'watermark_settings')],
            [Button.inline('⭕Close Settings', 'close_settings')]
        ])
            return
        
        elif txt=="close_settings":
            await event.delete()
            return
        
        elif txt.startswith("resetdb"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                reset = await resetdatabase(SAVE_TO_DATABASE)
                if reset:
                    text = f"✔Database Reset Successfull"
                else:
                    text = f"❌Database Reset Failed"
                await event.answer(text, alert=True)
            else:
                await event.answer(f"Why You Wasting My Time.", alert=True)
            return
        
        
        elif txt.startswith("renew"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                g_d_list = ['app.py','sample_config.env','start.sh','.gitignore','LICENSE','README.md', 'sthumb.jpg','Logging.txt', 'db_handler.py', 'config.py', 'bot', 'requirements.txt', 'Dockerfile', 'config.env', 'helper_fns', 'docker-compose.yml', 'thumb.jpg', 'main.py', 'userdata']
                g_list = listdir()
                g_del_list = list(set(g_list) - set(g_d_list))
                deleted = []
                if len(g_del_list) != 0:
                    for f in g_del_list:
                        if isfile(f):
                            if not(f.endswith(".session")) and not(f.endswith(".session-journal")):
                                print(f)
                                await delete_trash(f)
                                deleted.append(f)
                        else:
                            print(f)
                            await delete_all(f)
                            deleted.append(f)
                    text = f"✔Deleted {len(deleted)} objects 🚮\n\n{str(deleted)}"
                    try:
                            await event.answer(text, alert=True)
                    except:
                        await event.edit(text)
                else:
                    await event.answer(f"Nothing to clear 🙄", alert=True)
                    return
            else:
                await event.answer(f"Why You Wasting My Time.", alert=True)
                return
        
        elif txt.startswith("general"):
            new_position = txt.split("_", 1)[1]
            r_config = f'./userdata/{str(userx)}_rclone.conf'
            check_config = exists(r_config)
            drive_name = USER_DATA()[userx]['drive_name']
            edit = True
            if txt.startswith("generalselectstream"):
                await saveoptions(userx, 'select_stream', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Auto Select Audio - {str(new_position)}")
            elif txt.startswith("generalstream"):
                await saveoptions(userx, 'stream', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Select Audio - {str(new_position)}")
            elif txt.startswith("generalsplitvideo"):
                await saveoptions(userx, 'split_video', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Split Video - {str(new_position)}")
            elif txt.startswith("generalsplit"):
                await saveoptions(userx, 'split', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Split Size - {str(new_position)}")
            elif txt.startswith("generalcustomthumbnail"):
                await saveoptions(userx, 'custom_thumbnail', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Custom Thumbnail - {str(new_position)}")
            elif txt.startswith("generalcustommetadata"):
                if eval(new_position):
                        metadata = await get_metadata(user_id, userx, event, 120, "Send Metadata Title")
                        if metadata:
                            await saveoptions(userx, 'metadata', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(userx, 'custom_metadata', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Custom Metadata - {str(new_position)}")
            elif txt.startswith("generalcustomname"):
                await saveoptions(userx, 'custom_name', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Custom Name - {str(new_position)}")
            elif txt.startswith("generaluploadtg"):
                if not eval(new_position):
                    if not (check_config and drive_name):
                        await event.answer(f"❗First Save Rclone ConfigFile/Account", alert=True)
                        return
                await saveoptions(userx, 'upload_tg', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Upload On TG - {str(new_position)}")
            elif txt.startswith("generaldrivename"):
                await saveoptions(userx, 'drive_name', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Rclone Account - {str(new_position)}")
            elif txt.startswith("generalautodrive"):
                if eval(new_position):
                    if not (check_config and drive_name):
                        await event.answer(f"❗First Save Rclone ConfigFile/Account", alert=True)
                        return
                await saveoptions(userx, 'auto_drive', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Auto Upload Big File To Drive - {str(new_position)}")
            elif txt.startswith("generalgenss"):
                await saveoptions(userx, 'gen_ss', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Screenshoots - {str(new_position)}")
            elif txt.startswith("generalssno"):
                await saveoptions(userx, 'ss_no', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅No Of Screenshoots - {str(new_position)}")
            elif txt.startswith("generalgensample"):
                await saveoptions(userx, 'gen_sample', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Sample Video - {str(new_position)}")
            select_stream = USER_DATA()[userx]['select_stream']
            stream = USER_DATA()[userx]['stream']
            split_video = USER_DATA()[userx]['split_video']
            split = USER_DATA()[userx]['split']
            upload_tg = USER_DATA()[userx]['upload_tg']
            custom_name = USER_DATA()[userx]['custom_name']
            custom_metadata = USER_DATA()[userx]['custom_metadata']
            custom_thumbnail = USER_DATA()[userx]['custom_thumbnail']
            drive_name = USER_DATA()[userx]['drive_name']
            auto_drive = USER_DATA()[userx]['auto_drive']
            gen_ss = USER_DATA()[userx]['gen_ss']
            ss_no = USER_DATA()[userx]['ss_no']
            gen_sample = USER_DATA()[userx]['gen_sample']
            # rclone = USER_DATA()[userx]['rclone']
            KeyBoard = []
            KeyBoard.append([Button.inline(f'🥝Auto Select Audio - {str(select_stream)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, select_stream, "generalselectstream", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍭Select Audio - {str(stream)}', 'nik66bots')])
            for board in gen_keyboard(['ENG', 'HIN'], stream, "generalstream", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🪓Split Video - {str(split_video)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, split_video, "generalsplitvideo", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🛢Split Size - {str(split)}', 'nik66bots')])
            for board in gen_keyboard(['2GB', '4GB'], split, "generalsplit", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🖼Custom Thumbnail - {str(custom_thumbnail)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, custom_thumbnail, "generalcustomthumbnail", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🪀Custom Metadata - {str(custom_metadata)} [Click To See]', 'custom_metedata')])
            for board in gen_keyboard(bool_list, custom_metadata, "generalcustommetadata", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🔖Custom Name - {str(custom_name)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, custom_name, "generalcustomname", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🧵Upload On TG - {str(upload_tg)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, upload_tg, "generaluploadtg", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🕹Auto Upload Big File To Drive - {str(auto_drive)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, auto_drive, "generalautodrive", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📷Generate Screenshoots - {str(gen_ss)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, gen_ss, "generalgenss", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎶No Of Screenshoots - {str(ss_no)}', 'nik66bots')])
            for board in gen_keyboard([3,5,7,10], ss_no, "generalssno", 4, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎞Generate Sample Video - {str(gen_sample)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, gen_sample, "generalgensample", 2, False):
                KeyBoard.append(board)
            if check_config:
                accounts = await get_config(r_config)
                if accounts:
                    KeyBoard.append([Button.inline(f'🔮Rclone Account - {str(drive_name)}', 'nik66bots')])
                    for board in gen_keyboard(accounts, drive_name, "generaldrivename", 2, False):
                        KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                await event.edit("⚙ General Settings", buttons=KeyBoard)
            else:
                await Client.send_message(user_id, "⚙ General Settings", buttons=KeyBoard)
            return
        
        elif txt.startswith("progress"):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("progressdetailedprogress"):
                await saveoptions(userx, 'detailed_messages', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Detailed Messages - {str(new_position)}")
            elif txt.startswith("progressshowstats"):
                await saveoptions(userx, 'show_stats', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Stats - {str(new_position)}")
            elif txt.startswith("progressshowbotuptime"):
                await saveoptions(userx, 'show_botuptime', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Botuptime - {str(new_position)}")
            elif txt.startswith("progressupdatetime"):
                await saveoptions(userx, 'update_time', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Progress Update Time - {str(new_position)} secs")
            elif txt.startswith("progressffmpeglog"):
                await saveoptions(userx, 'ffmpeg_log', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show FFMPEG Log - {str(new_position)}")
            elif txt.startswith("progressffmpegsize"):
                await saveoptions(userx, 'ffmpeg_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show FFMPEG Output File Size - {str(new_position)}")
            elif txt.startswith("progressffmpegptime"):
                await saveoptions(userx, 'ffmpeg_ptime', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Process Time - {str(new_position)}")
            elif txt.startswith("progressshowtime"):
                await saveoptions(userx, 'show_time', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Current Time - {str(new_position)}")
            detailed_messages = USER_DATA()[userx]['detailed_messages']
            show_stats = USER_DATA()[userx]['show_stats']
            update_time = USER_DATA()[userx]['update_time']
            show_botuptime = USER_DATA()[userx]['show_botuptime']
            ffmpeg_log = USER_DATA()[userx]['ffmpeg_log']
            ffmpeg_size = USER_DATA()[userx]['ffmpeg_size']
            ffmpeg_ptime = USER_DATA()[userx]['ffmpeg_ptime']
            show_time = USER_DATA()[userx]['show_time']
            KeyBoard.append([Button.inline(f'📋Show Detailed Messages - {str(detailed_messages)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, detailed_messages, "progressdetailedprogress", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📊Show Stats - {str(show_stats)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, show_stats, "progressshowstats", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'❤Show Botuptime - {str(show_botuptime)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, show_botuptime, "progressshowbotuptime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🛠Show FFMPEG Log - {str(ffmpeg_log)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, ffmpeg_log, "progressffmpeglog", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📀Show FFMPEG Output File Size - {str(ffmpeg_size)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, ffmpeg_size, "progressffmpegsize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⏲Show Process Time- {str(ffmpeg_ptime)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, ffmpeg_ptime, "progressffmpegptime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⌚Show Current Time- {str(show_time)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, show_time, "progressshowtime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⏱Progress Update Time - {str(update_time)} secs', 'nik66bots')])
            for board in gen_keyboard([5, 6, 7, 8, 9, 10], update_time, "progressupdatetime", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            await event.edit("⚙ Progress Bar Settings", buttons=KeyBoard)
            return
        
        
        elif txt.startswith("compression"):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("compressionencoder"):
                await saveconfig(userx, 'compress', 'encoder', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Compress Encoder - {str(new_position)}")
            elif txt.startswith("compressionpreset"):
                await saveconfig(userx, 'compress', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Compress Preset - {str(new_position)}")
            elif txt.startswith("compressioncopysub"):
                await saveconfig(userx, 'compress', 'copy_sub', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Compress Copy Subtitles - {str(new_position)}")
            elif txt.startswith("compressionmap"):
                await saveconfig(userx, 'compress', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Compress Map - {str(new_position)}")
            elif txt.startswith("compressioncrf"):
                await saveconfig(userx, 'compress', 'crf', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Compress CRF - {str(new_position)}")
            compress_encoder = USER_DATA()[userx]['compress']['encoder']
            compress_preset = USER_DATA()[userx]['compress']['preset']
            compress_crf = USER_DATA()[userx]['compress']['crf']
            compress_map = USER_DATA()[userx]['compress']['map']
            compress_copysub = USER_DATA()[userx]['compress']['copy_sub']
            KeyBoard.append([Button.inline(f'🍬Encoder - {str(compress_encoder)}', 'nik66bots')])
            for board in gen_keyboard(encoders_list, compress_encoder, "compressionencoder", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍄Copy Subtitles - {str(compress_copysub)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, compress_copysub, "compressioncopysub", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍓Map  - {str(compress_map)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, compress_map, "compressionmap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'♒Preset - {str(compress_preset)}', 'nik66bots')])
            for board in gen_keyboard(presets_list, compress_preset, "compressionpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⚡CRF  - {str(compress_crf)}', 'nik66bots')])
            for board in gen_keyboard(crf_list, compress_crf, "compressioncrf", 6, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            await event.edit("⚙ Compression Settings", buttons=KeyBoard)
            return

        elif txt.startswith("merge"):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("mergemap"):
                await saveconfig(userx, 'merge', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Merge Map - {str(new_position)}")
            merge_map = USER_DATA()[userx]['merge']['map']
            KeyBoard.append([Button.inline(f'🍓Map  - {str(merge_map)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, merge_map, "mergemap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            await event.edit("⚙ Merge Settings", buttons=KeyBoard)
            return
        
        elif txt.startswith("watermark"):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("watermarkencoder"):
                await saveconfig(userx, 'watermark', 'encoder', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Encoder - {str(new_position)}")
            elif txt.startswith("watermarkencode"):
                await saveconfig(userx, 'watermark', 'encode', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Use Encoder - {str(new_position)}")
            elif txt.startswith("watermarkposition"):
                await saveconfig(userx, 'watermark', 'position', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Position - {str(ws_name[new_position])}")
            elif txt.startswith("watermarksize"):
                await saveconfig(userx, 'watermark', 'size', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Size - {str(new_position)}")
            elif txt.startswith("watermarkpreset"):
                await saveconfig(userx, 'watermark', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Preset - {str(new_position)}")
            elif txt.startswith("watermarkcopysub"):
                await saveconfig(userx, 'watermark', 'copy_sub', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Copy Subtitles - {str(new_position)}")
            elif txt.startswith("watermarkmap"):
                await saveconfig(userx, 'watermark', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark Map - {str(new_position)}")
            elif txt.startswith("watermarkcrf"):
                await saveconfig(userx, 'watermark', 'crf', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Watermark CRF - {str(new_position)}")
            watermark_position = USER_DATA()[userx]['watermark']['position']
            watermark_size = USER_DATA()[userx]['watermark']['size']
            watermark_encoder = USER_DATA()[userx]['watermark']['encoder']
            watermark_encode = USER_DATA()[userx]['watermark']['encode']
            watermark_preset = USER_DATA()[userx]['watermark']['preset']
            watermark_crf = USER_DATA()[userx]['watermark']['crf']
            watermark_map = USER_DATA()[userx]['watermark']['map']
            watermark_copysub = USER_DATA()[userx]['watermark']['copy_sub']
            KeyBoard.append([Button.inline(f'🥽Position - {str(ws_name[watermark_position])}', 'nik66bots')])
            for board in gen_keyboard(list(ws_name.keys()), watermark_position, "watermarkposition", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🛸Size - {str(watermark_size)}', 'nik66bots')])
            for board in gen_keyboard(wsize_list, watermark_size, "watermarksize", 6, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎧Use Encoder - {str(watermark_encode)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, watermark_encode, "watermarkencode", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍬Encoder - {str(watermark_encoder)}', 'nik66bots')])
            for board in gen_keyboard(encoders_list, watermark_encoder, "watermarkencoder", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍄Copy Subtitles - {str(watermark_copysub)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, watermark_copysub, "watermarkcopysub", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍓Map  - {str(watermark_map)}', 'nik66bots')])
            for board in gen_keyboard(bool_list, watermark_map, "watermarkmap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'♒Preset - {str(watermark_preset)}', 'nik66bots')])
            for board in gen_keyboard(presets_list, watermark_preset, "watermarkpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⚡CRF  - {str(watermark_crf)}', 'nik66bots')])
            for board in gen_keyboard(crf_list, watermark_crf, "watermarkcrf", 6, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            await event.edit("⚙ Watermark Settings", buttons=KeyBoard)
            return
        
        elif txt=="nik66bots":
            await event.answer(f"⚡Bot By Sahil⚡", alert=True)
            return
        
        elif txt=="custom_metedata":
            cmetadata = USER_DATA()[userx]['metadata']
            await event.answer(f"✅Current Metadata: {str(cmetadata)}", alert=True)
            return
        return