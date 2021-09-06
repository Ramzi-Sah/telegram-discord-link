import os, threading, asyncio
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
        
        # handle NewMessage event
        @client.on(events.NewMessage(chats=self.CHANNEL))
        async def NewMessage(event):
            try:
                # if reply get reply id
                reply_id = -1
                if event.is_reply:
                    reply = await event.get_reply_message()
                    reply_id = reply.id

                if event.photo:
                    # create file
                    file_path = "images/"
                    directory = os.path.dirname(file_path)

                    try:
                        os.stat(directory)
                    except:
                        os.mkdir(directory)
                    
                    path = await event.download_media(file_path)
                    print('File saved to', path)

                    # send to discord bot thread
                    self.data.put(
                        {
                            "type":"MESSAGE_NEW_TEXTIMAGE",
                            "msg_id": str(event.id),
                            "reply_id": str(reply_id),
                            "value": str(event.text),
                            "path": str(path)
                        }
                    )
                else:
                    # send to discord bot thread
                    self.data.put(
                        {
                            "type":"MESSAGE_NEW_TEXT", 
                            "msg_id": str(event.id),
                            "reply_id": str(reply_id),
                            "value": str(event.text)
                        }
                    )
            except Exception as e:
                print("[ERROR] on new Telegram message: " + str(e))

        # handle MessageEdited event
        @client.on(events.MessageEdited)
        async def MessageEdited(event):
            try:
                # if reply get reply id
                reply_id = -1
                if event.is_reply:
                    reply = await event.get_reply_message()
                    reply_id = reply.id

                if event.photo:
                    # create file
                    file_path = "images/"
                    directory = os.path.dirname(file_path)

                    try:
                        os.stat(directory)
                    except:
                        os.mkdir(directory)
                    
                    path = await event.download_media(file_path)
                    print('File saved to', path)

                    # send to discord bot thread
                    self.data.put(
                        {
                            "type":"MESSAGE_EDITED_TEXTIMAGE",
                            "msg_id": str(event.id),
                            "reply_id": str(reply_id),
                            "value": str(event.text),
                            "path": str(path)
                        }
                    )
                else:
                    # send to discord bot thread
                    self.data.put(
                        {
                            "type":"MESSAGE_EDITED_TEXT", 
                            "msg_id": str(event.id),
                            "reply_id": str(reply_id),
                            "value": str(event.text)
                        }
                    )
            except Exception as e:
                print("[ERROR] on edit Telegram message: " + str(e))


        await client.start()
        await client.run_until_disconnected()

    def run(self):
        asyncio.run(self.main())
