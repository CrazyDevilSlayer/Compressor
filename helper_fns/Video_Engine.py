from helper_fns.Helper import USER_DATA, clear_trash_list, delete_trash, get_video_duration
from helper_fns.FFMPEG_Engine import ffmpeg_engine
from math import ceil
from os.path import getsize, join
from config import Config


#////////////////////////////////////Variables////////////////////////////////////#
LOGGER = Config.LOGGER



#////////////////////////////////////Video_Engine////////////////////////////////////#
class Processor:
    ###############------Compressor------###############
    async def compress(Client, reply, user_id, userx, input_file, progress, amap_options, output_file, duration, check_data, datam):
        compress_encoder = USER_DATA()[userx]['compress']['encoder']
        compress_preset = USER_DATA()[userx]['compress']['preset']
        compress_crf = USER_DATA()[userx]['compress']['crf']
        compress_map = USER_DATA()[userx]['compress']['map']
        compress_copysub = USER_DATA()[userx]['compress']['copy_sub']
        command = ['ffmpeg','-hide_banner',
                                    '-progress', f"{progress}",
                                    '-i', f'{str(input_file)}']
        if compress_map:
            command+=['-map','0:v?',
                                        '-map',f'{str(amap_options)}?',
                                        "-map", "0:s?"]
        if compress_copysub:
            command+= ["-c:s", "copy"]
        if compress_encoder=='libx265':
                command+= ['-vcodec','libx265','-vtag', 'hvc1']
        else:
                command+= ['-vcodec','libx264']
        command+= ['-preset', compress_preset, '-crf', f'{str(compress_crf)}', '-y', f'{str(output_file)}']
        datam.append(f'🏮Compressing Video')
        result = await ffmpeg_engine(Client, user_id, userx, reply, command, input_file, output_file, progress, duration, check_data, datam, True)
        if result[0]:
            if result[1]:
                await reply.edit("🔒Task Cancelled By User")
                return False
            return True
        else:
            return False

    ###############------Split_Video------###############
    async def split_video_file(Client, new_event, user_id, userx, reply, split_size, dirpath, file, file_name, progress, duration, datam, check_data, extension):
        success = []
        trash_list = []
        datam.append(f'🪓Spliting Video')
        try:
            size = getsize(file)
            parts = ceil(size/split_size)
            i=1
            start_time = 0
            while i <= parts:
                    file_name = file_name.replace(f".{str(extension)}", "").replace(str(extension), "")
                    parted_name = f"{str(file_name)}.part{str(i).zfill(3)}.{str(extension)}"
                    datam[0] = parted_name
                    out_path = join(dirpath, parted_name)
                    trash_list.append(out_path)
                    command = ["ffmpeg", "-hide_banner", "-progress", f"{progress}", "-ss", str(start_time),
                                "-i", str(file), "-fs", str(split_size), "-map", "0", "-map_chapters", "-1",
                                "-c", "copy", f"{out_path}"]
                    result = await ffmpeg_engine(Client, user_id, userx, reply, command, file, out_path, progress, duration, check_data, datam, False)
                    if result[0]:
                            if result[1]:
                                    await clear_trash_list(trash_list)
                                    await reply.edit("🔒Task Cancelled By User")
                                    return False
                    else:
                            await delete_trash(out_path)
                            command = ["ffmpeg", "-hide_banner", "-progress", f"{progress}", "-ss", str(start_time),
                                "-i", str(file), "-fs", str(split_size), "-map_chapters", "-1",
                                "-c", "copy", out_path]
                            result = await ffmpeg_engine(Client, user_id, userx, reply, command, file, out_path, progress, duration, check_data, datam, False)
                            if result[0]:
                                    if result[1]:
                                            await clear_trash_list(trash_list)
                                            await reply.edit("🔒Task Cancelled By User")
                                            return False
                            else:
                                    await clear_trash_list(trash_list)
                                    return False
                    cut_duration = get_video_duration(out_path)
                    if cut_duration <= 4:
                            break
                    success.append(out_path)
                    start_time += cut_duration - 3
                    i = i + 1
            return success
        except Exception as e:
            await new_event.reply(f"❗Error While Splitting Video\n\n{str(e)}")
            await clear_trash_list(trash_list)
            print(e)
            LOGGER.info(str(e))
            return False