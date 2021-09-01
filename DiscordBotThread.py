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
            await self.client.start(self.TOKEN, bot=True)
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

        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="make us rich."))
        
        # get discord channel
        channel = self.client.get_channel(self.CHANNEL)
        if not channel:
            print("[ERROR] cannot find discord channel with id \"" + str(self.CHANNEL) + "\"")
            self.run = False
        else:
            print('########################################################')

        # wait for telegram thread data
        while self.run:
            data = await self.data.aget()
            # data["value"] += " @everyone"

            try:
                type = data["type"].split("_")

                # handle message
                if type[0] == "MESSAGE":
                    # new message
                    if type[1] == "NEW":
                        # text message
                        if type[2] == "TEXT":
                            # create embed
                            embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                            embed.set_footer(text="# " + data["msg_id"])

                            # send the message
                            await channel.send(embed=embed)

                        # text & image message
                        elif type[2]== "TEXTIMAGE":
                            # create discord file
                            filename = "from_telegram." + data["path"].split(".")[-1]
                            file = discord.File(data["path"], filename=filename)

                            # create embed
                            embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                            embed.set_image(url="attachment://" + filename)
                            embed.set_footer(text="# " + data["msg_id"])

                            # send the message
                            await channel.send(embed=embed, file=file)
                        
                        print("message #" + data["msg_id"] + " forwarded successfully.")
                    
                    # edited message
                    elif type[1] == "EDITED":
                        # get the last 20 messages
                        async for message in channel.history(limit=20):
                            # check if message has an embed
                            if len(message.embeds) == 0: continue

                            # get the first message's embed
                            embed = message.embeds[0]

                            # check if message has id
                            if embed.footer.text == discord.Embed.Empty : continue
                            if len(embed.footer.text.split()) <= 1: continue

                            # get message id
                            msgID = embed.footer.text.split()[1]
                            if msgID == data["msg_id"]:
                                # new message
                                if type[2] == "TEXT":
                                    # create embed
                                    embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                                    embed.set_footer(text="# " + data["msg_id"])

                                    # update the message
                                    await message.edit(embed=embed)

                                # text & image message
                                elif type[2]== "TEXTIMAGE":
                                    # create discord file
                                    filename = "from_telegram." + data["path"].split(".")[-1]
                                    file = discord.File(data["path"], filename=filename)

                                    # create embed
                                    embed = discord.Embed(description=data["value"], color=discord.Color.blue())
                                    embed.set_image(url="attachment://" + filename)
                                    embed.set_footer(text="# " + data["msg_id"])
                                    
                                    # update the message
                                    await message.edit(embed=embed)

                                print("message #" + data["msg_id"] + " edited successfully.")
                                break



            except Exception as e:
                print("[ERROR] could not forward the discord message: " + str(e))

            # task_done signal
            self.data.task_done()
