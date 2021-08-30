import threading, asyncio
import discord

class DiscordBotThread(threading.Thread):
    def __init__(self, TOKEN, CHANNEL, data):
        threading.Thread.__init__(self)
        
        self.TOKEN = TOKEN
        self.CHANNEL = CHANNEL

        self.data = data
        self.run = True

        self.client = discord.Client()

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.main())
        self.loop.create_task(self.main_loop())
        self.loop.run_forever()
        
        self.start()

    async def main(self):
        try:
            await self.client.start(self.TOKEN, bot=False)
        except Exception as e:
            print("[ERROR] couldn't login on discord: " + str(e))
    
    async def main_loop(self):
        await self.client.wait_until_ready()
                
        # check if telegram thread is ok
        data = self.data.get()

        if data == "TELEGRAM_THREAD_STARTED":
            print("discord bot thread started.")
            print(f'connected to Discord as \"{self.client.user}\"')
        else:
            self.run = False

        self.data.task_done()

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Make me rich"))
        
        # get discord channel
        channel = self.client.get_channel(self.CHANNEL)
        if not channel:
            print("[ERROR] cannot find discord channel with id \"" + str(self.CHANNEL) + "\"")
            self.run = False
        else:
            print('########################################################')

        
        # wait for telegram thread data
        while self.run:
            data = self.data.get()
            data["value"] += " @everyone"

            try:
                # send message to discord channel
                if data["type"] == "text":
                    embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                    await channel.send(embed=embed)

                elif data["type"] == "image, text":
                    filename = "from_telegram." + data["path"].split(".")[-1]
                    file = discord.File(data["path"], filename=filename)

                    embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                    embed.set_image(url="attachment://" + filename)

                    await channel.send(embed=embed, file=file)
                
                print("message forwarded successfully.")

            except Exception as e:
                print("Error sending discord message: " + str(e))

            # task_done signal
            self.data.task_done()
