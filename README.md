# A Multi-Feature Telegram Bot


### Configuration
To configure this bot add the environment variables stated below. Or add them in [sample_config.env](./sample_config.env) and change the name to `config.env`.
- `API_ID` - (Required)Get it by creating an app on [https://my.telegram.org](https://my.telegram.org)
- `API_HASH` - (Required)Get it by creating an app on [https://my.telegram.org](https://my.telegram.org)
- `TOKEN` - (Required)Get it by creating a bot on [https://t.me/BotFather](https://t.me/BotFather)
- `SUDO_USERS` - (Required)Chat identifier list of the sudo user.
- `RESTART_NOTIFY_ID` - (Required)Numerical chat id of user , group or channel to notify on bot restart, set it False if you don't want notification on start.
- `SAVE_TO_DATABASE` - (Required)Set value True if you want to use MongoDB Database else False.
- `MONGODB_URI` - (Optional)MongoDB URL to save data, only required when SAVE_TO_DATABASE's value is True.
- `CREDIT` - (Optional)Credit Name, only required when SAVE_TO_DATABASE's value is True [changing this will also change your database].
- `BOT_USERNAME` - (Optional)Bot Username without @, only required when SAVE_TO_DATABASE's value is True.
- `Use_Session_String` - (Required)Set value True if you want to use Telegram user session string to upload 4GB file to telegram else False.
- `Session_String` - (Optional)Telethon Session String, only required when Use_Session_String's value is True.

### Commands
```
compress - Compress Video
merge - Merge Video
watermark - Add Watermark To Video
savewatermark - Save Watermark Image
queue - To Start/Process Queue
clearqueue - Clear All Queued Tasks
terminatequeue - Terminate Queued Tasks
clearonequeue - Clear Only One Queued Task
getqueue - Get Queued Tasks Details
saveconfig - Save Rclone Config
addsudo - Add New Sudo User
delsudo - Delete Sudo User
getsudo - Get Sudo Users List
log - Get Log Message
logs - Get Log File
resetdb - Reset Database
renew - Renew Storage
time - Get Bot Uptime
settings - Settings Section
restart - Restart Bot
```



### Copyright & License
- Copyright &copy; 2023 &mdash; [Nik66](https://github.com/sahilgit55)
- Licensed under the terms of the [GNU General Public License Version 3 &dash; 29 June 2007](./LICENSE)