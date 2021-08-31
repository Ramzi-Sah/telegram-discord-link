# https://stackoverflow.com/questions/55829852/how-to-communicate-between-traditional-thread-and-asyncio-thread-in-python

import asyncio
import queue

class nonBlockingQueue(queue.Queue):
    def __init__(self, qSize):
        super().__init__(qSize)
        self.timeout=0.018

    async def aget(self):
        while True:
            try:
                return self.get_nowait()
            except queue.Empty:
                await asyncio.sleep(self.timeout)
            except Exception as E:
                raise

    async def aput(self,data):
        while True:
            try:
                return self.put_nowait(data)
            except queue.Full:
                await asyncio.sleep(self.timeout)
            except Exception as E:
                raise
