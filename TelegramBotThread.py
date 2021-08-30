import threading, asyncio
from telethon import TelegramClient, events

class TelegramBotThread(threading.Thread):
    def __init__(self, API_ID, API_HASH, CHANNEL, data):
        threading.Thread.__init__(self)

        self.API_ID = API_ID
        self.API_HASH = API_HASH
        self.CHANNEL = CHANNEL

        self.data = data

        self.start()

    async def main(self):
        client = TelegramClient('anon', self.API_ID, self.API_HASH)

        async with client:
            print("telegram bot thread started.")

            me = await client.get_me()
            print(f'logged in as \"{me.username}\" on Telegram')

            if self.CHANNEL == 0:
                self.data.put("TELEGRAM_THREAD_NOT_OK")
                
                print("liste des channels: ")
                async for dialog in client.iter_dialogs():
                    print('\t' + str(dialog.name) + '| ID: ' + str(dialog.id))
                
                exit()
            else:
                self.data.put("TELEGRAM_THREAD_STARTED")

            entity = await client.get_entity(self.CHANNEL)
            print("listening to channel: \"" + entity.title + "\".")

            # await client.send_message(self.CHANNEL, 'hello world')
            
            """
            async for message in client.iter_messages(self.CHANNEL):
                self.data.put(str(message.text))
            """
        
        # respond to messages
        @client.on(events.NewMessage(chats=self.CHANNEL))
        async def NewMessage(event):
            try:
                if event.photo:
                    path = await event.download_media(".\\images")
                    print('File saved to', path)

                    # send to discord bot thread
                    self.data.put(
                        {
                            "type":"image, text", 
                            "value": str(event.text), 
                            "path": str(path)
                        }
                    )
                else:
                    # send to discord bot thread
                    self.data.put({"type":"text", "value": str(event.text)})

            except Exception as e:
                print("Error on Telegram message: " + str(e))
            
        await client.start()
        await client.run_until_disconnected()

    def run(self):
        asyncio.run(self.main())