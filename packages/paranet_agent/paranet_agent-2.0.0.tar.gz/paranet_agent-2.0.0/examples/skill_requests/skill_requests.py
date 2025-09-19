import base64
import asyncio

from paranet_agent import actor, connector
from paranet_agent.actor import BaseActor, Conversation


######## Skill data types

## uuid/generate skill request/response types

@actor.type
class UuidResponse:
  id: str

@actor.skill_request(subject='uuid', action='generate', response=UuidResponse)
class UuidRequest:
  data: str

## greeter/greet skill response type

@actor.type
class GreetResponse:
  greeting: str


######## Greeter actor

@actor.actor
class Greeter(BaseActor):
  @actor.skill(response=GreetResponse, background=True)
  def greet(self, name: str, conv: Conversation) -> None:
    asyncio.ensure_future(self.greet_task(name, conv))

  async def greet_task(self, name: str, conv: Conversation):
    res = await self.send_request(UuidRequest(data=name))
    id = res.id
    conv.send_response(GreetResponse(greeting=f'Hello {name} {id}'))


######## UuidGen actor

@actor.actor
class UuidGen(BaseActor):
  @actor.skill(subject='uuid', action='generate')
  def get_uuid(self, data: str) -> UuidResponse:
    id = base64.b64encode(bytes(data, encoding='utf-8'))
    return UuidResponse(id=id.decode('utf-8'))


########## Startup

# Create an instance of the actor and register it

actor.register_actor(Greeter(), requests=[UuidRequest])
actor.register_actor(UuidGen())

# Start connector service
connector.start()

# Deploy all actors
actor.deploy('skill_requests')

# Run a main loop
loop = asyncio.events.get_event_loop()
loop.run_until_complete(connector.get_task())