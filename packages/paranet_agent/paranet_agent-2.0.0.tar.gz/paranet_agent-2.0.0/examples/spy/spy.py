import asyncio

from paranet_agent import actor, connector
from paranet_agent.actor import BaseActor

########## Greeter
# This is the actor from the hello_python example that we'll spy on

@actor.type
class Greeting:
  message: str

# Declare the actor class

@actor.actor
class Greeter(BaseActor):
  @actor.skill
  def greet(self, name: str) -> Greeting:
    return Greeting(message = 'HELLO ' + name)


########## Spy

# Declare an actor class that observes the greeting skill provided
# by the above Greeter actor.

@actor.actor
class Spy(BaseActor):
  @actor.observation(subject='greeter',action='greet')
  def watch_greet(self, name: str) -> None:
    print('I see you ' + name + '!!!')


########## Startup

# Create an instance of the actor and register it

actor.register_actor(Greeter())
actor.register_actor(Spy())

# Start connector service
connector.start()

# Deploy all actors
actor.deploy('spy_py')

# Run a main loop
loop = asyncio.events.get_event_loop()
loop.run_until_complete(connector.get_task())