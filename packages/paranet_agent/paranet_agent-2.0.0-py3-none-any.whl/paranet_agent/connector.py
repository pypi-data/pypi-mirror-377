"""
# Connector API

The connector API is used to start the agent runtime which is a web service the Paranet
will use to interact with your actors.

The runtime should be started **after** you've registered your actors, but **before** you deploy
them.

After you've registered actors, started the runtime and deployed actors, the main thread should
just wait on the runtime task as follows:

```python
loop = asyncio.events.get_event_loop()
loop.run_until_complete(connector.get_task())
```

@doc:fmt:google
"""

import asyncio
from aiohttp import web

from .paraflow import use_external_paraflow

class Server:
    """@private GraphQL server"""

    _instance = None

    @staticmethod
    def get_instance():
        if not Server._instance:
            raise Exception('Bridge API not started')
        return Server._instance

    def __init__(self, port):
        self.port = port
        self.stopping = False
        self.task = None
        self.view = None

    def start(self):
        previous = Server._instance
        if previous and not previous.stopping:
            raise Exception('Bridge API already started')
        Server._instance = self
        self.task = asyncio.ensure_future(self.launch(previous))

    def stop(self):
        self.stopping = True
        self.task.cancel()

    async def launch(self, previous):
        if previous:
            await previous.task
        await self.serve()

    async def serve(self):
        print('Starting bridge API')
        try:
            handler = self.handler.__get__(self, Server)
            server = web.Server(handler)
            runner = web.ServerRunner(server)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            print('Bridge API stopped')
            await runner.cleanup();
        except Exception as err:
            print('Bridge API error', err)

    async def handler(self, request):
        if request.path == '/graphql':
            return await self.view(request)
        elif request.path == '/shutdown':
            self.task.cancel()
        return web.Response(status=404,text=request.path + ' not found')

    def get_task(self):
        return self.task

    def set_graphql_view(self, view):
        self.view = view

def get_task():
    """
    Get the asyncio Task running the connector service.  Use this method in the main
    thread.

    Example:
    ```python
    loop = asyncio.events.get_event_loop()
    loop.run_until_complete(connector.get_task())    
    ```

    Returns:
      A future that represents the runtime connector service.

    """
    return Server.get_instance().get_task()

def start(port: int = 3000):
    """
    Start the connector service.  The connector service is an HTTP server that allows the Paranet to communicate with the Python actors.

    Args:
      port: The port number the runtime service listens to (default: 3000)
    """
    server = Server(3000 if use_external_paraflow() else port)
    server.start()

def stop():
    """Stop the connector service."""
    Server.get_instance().stop()
