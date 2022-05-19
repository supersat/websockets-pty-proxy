#!/usr/bin/env python3

from aiohttp import web
import asyncio
import os
import pty
import tty

class WebsocketPTYProxy:
    def __init__(self, **kwargs):
        self._app = web.Application()
        self._app.add_routes([web.get('/pppd', self.get_pppd)])
        self._buffer_size = 1024

    async def handle_stdout(self, ws, p):
        while not p.stdout.at_eof():
            data = await p.stdout.read(self._buffer_size)
            if len(data):
                await ws.send_bytes(data)
        await ws.write_eof()

    async def get_pppd(self, request):
        # TODO: Check authentication cookies

        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)

        try:
            pppd = await asyncio.create_subprocess_exec("/usr/bin/socat",
                "stdio", "exec:pppd,pty",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE)

            asyncio.ensure_future(self.handle_stdout(ws, pppd))

            async for msg in ws:
                await stdin.write(msg.data)

        except Exception as ex:
            print(ex)
        finally:
            return ws

    def run(self):
        web.run_app(self._app)

def main():
    daemon = WebsocketPTYProxy()
    daemon.run()

if __name__ == '__main__':
    main()
