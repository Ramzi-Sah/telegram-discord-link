########################################################
# for telegram
TELEGRAM_API_ID = 0
TELEGRAM_API_HASH = ''
TELEGRAM_CHANNEL = 0

# for discord
DISCORD_TOKEN = ""
DISCORD_CHANNEL = 0



########################################################
# for threads communication
import queue
data = queue.Queue()

########################################################
# start the telegram bot thread
import TelegramBotThread
TelegramBotThread.TelegramBotThread(TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_CHANNEL, data)

########################################################
# start the discord bot thread
import DiscordBotThread
DiscordBotThread.DiscordBotThread(DISCORD_TOKEN, DISCORD_CHANNEL, data)
