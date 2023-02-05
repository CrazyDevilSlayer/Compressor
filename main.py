from config import Config
from sys import modules
from importlib.util import spec_from_file_location, module_from_spec
from helper_fns.Helper import clear_restart
from pathlib import Path
from glob import glob

#////////////////////////////////////Variables////////////////////////////////////#
working_dir = "./bot"
files = glob(f'{working_dir}/*.py')
User_Data = Config.User_Data
sudo_users = Config.SUDO_USERS


###############------Load_Plugins------###############
def load_plugins(plugin_name):
    path = Path(f"{working_dir}/{plugin_name}.py")
    name = "main.plugins.{}".format(plugin_name)
    spec = spec_from_file_location(name, path)
    load = module_from_spec(spec)
    spec.loader.exec_module(load)
    modules["main.plugins." + plugin_name] = load
    print("🔷Successfully Imported " + plugin_name)
    return

###############------Get_Plugins------###############
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name.replace(".py", ""))

###############------Get_Client_Details-----###############
async def get_me(client):
    return await client.get_me()


###############------Check_Restart------###############
async def check_restart():
    try:
        chat, msg_id = User_Data['restart'][0]
        await clear_restart()
        await Config.client.edit_message(chat, msg_id, '✅Restarted Successfully')
    except Exception as e:
        print("🧩Error While Updating Restart Message:\n\n", e)
    return

###############------Start_User_Session------###############
def start_user_account():
    Config.USER.start()
    user = Config.client.loop.run_until_complete(get_me(Config.USER))
    first_name = user.first_name
    if not user.premium:
        print(f"⛔User Account {first_name} Don't Have Telegram Premium, 2GB Limit Will Be Used For Telegram Uploading.")
    else:
        print(f"💎Telegram Premium Found For  User {first_name}")
    print(f'🔒Session For {first_name} Started Successfully!🔒')
    return

###############------Restart_Notification------###############
async def notify_restart(RESTART_NOTIFY_ID):
    try:
        await Config.client.send_message(RESTART_NOTIFY_ID, "⚡Bot Started Successfully⚡")
    except Exception as e:
        print("❗Failed To Send Restart Notification ", e)
    return


if __name__ == "__main__":
    Config.client.start(bot_token=Config.TOKEN)
    bot = Config.client.loop.run_until_complete(get_me(Config.client))
    if Config.SAVE_TO_DATABASE and 'restart' in User_Data and len(User_Data['restart']):
        Config.client.loop.run_until_complete(check_restart())
    elif Config.RESTART_NOTIFY_ID:
        Config.client.loop.run_until_complete(notify_restart(Config.RESTART_NOTIFY_ID))
    if Config.USER:
        start_user_account()
    print(f'✅@{bot.username} Started Successfully!✅')
    print(f"⚡Bot By Sahil Nolia⚡")
    Config.client.run_until_disconnected()