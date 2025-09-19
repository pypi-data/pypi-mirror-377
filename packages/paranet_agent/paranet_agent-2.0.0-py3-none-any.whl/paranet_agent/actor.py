import copy
import uuid
import inspect
import builtins
import asyncio
import dataclasses
import functools
import typing
import json as json_util
from typing import Optional, Union, get_type_hints
import requests

import strawberry
from strawberry.types.field import StrawberryField
from strawberry.types.arguments import StrawberryArgument
from strawberry.aiohttp.views import GraphQLView
from strawberry.annotation import StrawberryAnnotation

from .version import __version__
from .connector import Server
from .deployment import launch_actors
from .paraflow import PARAFLOW_HOST, use_external_paraflow
from .gql import *
from .decorations import get_action, get_subject
from .metadata import Actor, build_actor
from .marshalling import import_paraflow_object

# set at launch
prj_name = None


#################### decorators

class SkillField:
    def __init__(self, subject, action, response=False, observe=False, bg=None, skillset=None, instance_param=None):
        self.skillset = skillset
        self.subject = subject
        self.action = action
        self.response = response
        self.observe = observe
        self.bg = bg
        self.instance_param = instance_param


def type(cls = None):
    """Annotates a class as a Paranet data type.  This annotation is required on the following types:
    * All skill handler method return or response types
    * Skill request response types
    * Nested classes in skill return, skill request, and broadcast types

    The supported field types include:
    * scalar types (int, float, str)
    * user-defined classes also annotated with the `type` decorator
    * lists of a user-defined classes (scalar fields only) also annotated with the `type` decorator

    Example type annotation:

    ```python
    @actor.type
    class Location:
        lat: float
        lon: float
    ```
    """

    def wrap(cls):
        sb = strawberry.type(cls)
        return sb

    if cls == None:
        return wrap

    return wrap(cls)

def input(cls = None):
    """Annotates a class as a Paranet input data type.  This annotation is required on any class used as an argument to a skill method.

    The supported field types include:
    * scalar types (int, float, str)

    Example input annotation:

    ```python
    @actor.input
    class Location:
        lat: float
        lon: float
    ```
    """

    def wrap(cls):
        sb = strawberry.input(cls)
        return sb

    if cls == None:
        return wrap

    return wrap(cls)


def actor(cls = None, *, name=None, subject=None):
    """Annotates a class as an actor.  The class must extend the `BaseActor` class.

    Use the following decorator arguments to configure the actor class:

    - `name` The name of the actor on the Paranet (optional).  If not provided, defaults to the class name in lower case.
    - `subject` The default actor subject (optional).  Skills provided by this actor will have this subject if not specified
      in the `@actor.skill` decorator.  If not provided, the actor default subject will be the actor name.

    Example actor class:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.skill
        def echo(self, s: str) -> str:
            return s
    ```

    Since no arguments are provided the default actor name and subject default in this example is "myactor".
    Also, since no arguments are given to the skill method `echo`, the corresponding skill name would be "myactor/echo".
    """

    def wrap(cls):
        sb = strawberry.type(cls)
        actor_name = name or cls.__name__.lower()
        def get_name(instance):
            return actor_name
        sb.__actor_name__ = get_name
        sb.__subject__ = subject or actor_name
        return sb

    if cls == None:
        return wrap

    return wrap(cls)

def skill(fn = None, *, id=None, subject=None, action=None, background=None, response=None, instance_param=None):
    """Annotates a method as a skill request handler.  This actor will be registered as a provider
    for the corresponding skill and this method will be called when the actor receives a request
    for that skill.

    The advertised skill is defined by the:
    * subject/action arguments of this decorator
    * input parameters of the method
    * return type of the method or the response argument of this decorator

    The following decorator arguments are available to configure the skill/handler:
    - `subject` The skill subject (optional).  If not provided, defaults to the actor's subject.
    - `action` The skill action (optional).  If not provided, defaults to the name of the method.
    - `background` Indicates that the skill is asynchronous.
    - `response` The response type (implies background).  The type must be a class annotated with `@actor.type`.
    - `instance_param` The instance parameter (optional).  For multi-instance actors, this instance parameter contains an actor instance id.
    - `id` The id of a registered skillset that defines this skill.

    Example provided skill method:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.skill
        def echo(self, s: str) -> str:
            return s
    ```

    **Background skills using async**

    Skill request handlers **should not block** for long periods of time.  Long running skills can use an async method.  These are automatically
    converted to use `background`/`response` behind the scenes.

    Here's an async example:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.skill
        async def long_running(self, s: str) -> ResultData:
            await asyncio.sleep(10)
            return ResultData(status='done')
    ```
    """

    def wrap(fn):
        if inspect.iscoroutinefunction(fn):
            conv_param = None
            for k in fn.__annotations__:
                if fn.__annotations__[k] == Conversation:
                    conv_param = k
            if conv_param is None:
                raise Exception(f"Error: async skill {fn.__name__} must have a Conversation argument")

            async def perform_skill(*args, **kwargs):
                conv = kwargs[conv_param]
                try:
                  result = await fn(*args,**kwargs)
                  conv.send_response(result)
                except Exception as ex:
                  conv.background_error(str(ex))

            @functools.wraps(fn)
            def sync_fn(*args, **kwargs):
                asyncio.ensure_future(perform_skill(*args,**kwargs))
                return None
            
            bg_response = sync_fn.__annotations__['return']
            sync_fn.__annotations__['return'] = builtins.type(None)

            sb = strawberry.field(sync_fn)
            bg = True
        else:
            sb = strawberry.field(fn)
            bg = True if response != None else background
            bg_response = response
        sb.__skill__ = SkillField(subject, action or fn.__name__, bg=bg, response=bg_response, skillset=id, instance_param = instance_param)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

def observation(fn = None, *, subject, action):
    """Annotates a method as a skill observation handler.  This actor does not provide the skill, but merely watches
       requests for the given skill.  The handler is called whenever the skill is observed.  The method parameters must match
       the skill requests inputs.  The method must have a return type None.

    - `subject` The observed skill's subject (required).
    - `action` The The observed skill's action (required).

    Example observation handler:

    ```python
    @actor.actor
    class MyActor(BaseActor):
        @actor.observation(subject='order',action='new_order')
        def handle_new_order(self, order: Order) -> None:
            ...
    ```
    """

    def wrap(fn):
        sb = strawberry.field(fn)
        sb.__skill__ = SkillField(subject, action or fn.__name__, observe=True)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

# This is undocumented, maybe remove?  Not sure if there is a use case.

def skill_response(fn = None, *, action=None, subject=None):
    def wrap(fn):
        sb = strawberry.field(fn)
        sb.__skill__ = SkillField(subject, action or fn.__name__, response=True)
        return sb

    if fn == None:
        return wrap

    return wrap(fn)

def skill_request(cls = None, *, subject: str, action: str, response=None):
    """Annotates a class as a Paranet skill request _input signature_.  Actors that make
    skill requests must declare the skills they intend to use by defining a class with the
    `skill_request` annotation that you provide when you register the actor (see `register`
    method).  Note that the input schema for the skill corresponds to the fields of this class,
    not the actual class itself.  To make the skill request, you will call the `send_request` method
    with an instance of this class as the inputs for your request.

    - `subject` The subject of skill request (required).
    - `action` The action of skill request (required).
    - `response` A class corresponding to the response schema of the skill request which must be annotated with `type`.

    The supported field types include:
    * scalar types (int, float, str)
    * user-defined classes also annotated with the `type` decorator
    * lists of a user-defined classes (scalar fields only) also annotated with the `type` decorator
    
    Example skill request class:

    ```python
    @actor.skill_request(subject='occupancy', action='query')
    class Location:
        lat: float
        lon: float
    ```

    The corresponding skill definition is
    ```yaml
      subject: occupancy
      actions:
        - action: query
          input:
            lat: paranet:number
            lon: paranet:number
    """

    def wrap(cls):
        if response:
            if not dataclasses.is_dataclass(response):
                raise Exception('ERROR %s is missing @actor.type class decorator' % (response.__name__,))
  
        dc = dataclasses.dataclass(cls)
        dc.__subject__ = subject
        dc.__action__ = action
        dc.__response__ = response
        dc.__registered__ = False
        return dc

    if cls == None:
        return wrap

    return wrap(cls)

def broadcast(cls = None, *, subject: str=None, action: str):
    """Annotates a class as a Paranet broadcast request _input signature_.  Actors that make
    broadcast requests must declare the broadcasts they intend to use by defining a class with this
    `broadcast` annotation that you provide when you register the actor (see `register`
    method).  Note that the input schema for the broadcast corresponds to the fields of this class,
    not the actual class itself.  To make the broadcast request, you will call the `send_broadcast` method
    with an instance of this class as the inputs for your request.

    - `subject` The subject of broadcast (required).
    - `action` The action of broadcast (required).

    The supported field types include:
    * scalar types (int, float, str)
    * user-defined classes also annotated with the `type` decorator
    * lists of a user-defined classes (scalar fields only) also annotated with the `type` decorator

    Example broadcast skill class:

    ```python
    @actor.broadcast(subject='nav', action='current_location')
    class Location:
        lat: float
        lon: float
    ```

    The corresponding broadcast definition is
    ```yaml
      subject: nav
      actions:
        - action: current_location
          input:
            lat: paranet:number
            lon: paranet:number
    ```
    """

    def wrap(cls):
        dc = dataclasses.dataclass(cls)
        dc.__subject__ = subject
        dc.__action__ = action
        return dc

    if cls == None:
        return wrap

    return wrap(cls)


#################### globals

noneType = builtins.type(None)

actor_registry = {}
actor_instances = {}

pending_requests = {}
pending_responses = {}
pending_errors = {}

def post_event(prj_name, actor, name, body):
    # this is required to serialize as json
    for k in body:
        if dataclasses.is_dataclass(body[k]):
            body[k] = dataclasses.asdict(body[k])

    path_prefix = '/event/' if use_external_paraflow() else '/extern/actors/%s-%s/event/' % (prj_name, actor)
    url = PARAFLOW_HOST + path_prefix + name
    res = requests.post(url, json = body)
    try:
        resp = res.json()
    except:
        print(f'ERROR event {url}({body}) failed')
        print(res.text)
        raise Exception('Fatal error') from None
    if 'errors' in resp:
        print(f'ERROR event {url}({body}) failed')
        for e in resp['errors']:
            print('\t'+e)
        raise Exception('Fatal error') from None
    return resp

def handle_skill_response(uid, obj):
    if uid in pending_requests:
        inst = pending_requests[uid]
        inst.set_response(obj)
        del pending_requests[uid]

def lookup_skill_response(cid):
    if cid in pending_responses:
        resp = pending_responses[cid]
        del pending_responses[cid]
        return resp
    elif cid in pending_errors:
        err = pending_errors[cid]
        del pending_errors[cid]
        raise Exception(err)


#################### Run-time classes

class Conversation:
    """Represents an instance of a skill request"""

    actor: str
    """@private actor name"""

    event: str
    """@private completion event"""

    cid: str
    """Paranet conversation ID"""

    def __init__(self, actor, event, cid):
        """@private constructor"""
        self.actor = actor
        self.event = event
        self.cid = cid

    def __repr__(self):
        return 'Conversation(%s,%s)' % (self.actor, self.cid)

    def send_status(self, data):
        """Send skill request status"""
        name = data.__class__.__name__
        event = event_api_name(SEND_EVENT, self.actor, name, '')
        body = {'_cid': self.cid}
        body.update(dataclasses.asdict(data))
        post_event(prj_name, self.actor, event, body)

    def send_complete(self):
        """Send notification of background skill's completion"""
        body = {'cid': self.cid}
        post_event(prj_name, self.actor, self.event, body)

    def send_response(self, data):
        """Send the response from a background skill request"""
        pending_responses[self.cid] = data
        self.send_complete()

    def background_error(self, error: str):
        """@private propagate error"""
        pending_errors[self.cid] = error
        self.send_complete()

class BaseActor:
    """Base class for all actors"""

    def __init__(self):
        pass
    
    def __actor_name__():
        raise Exception('Invalid call on base class')

    def send_request(self, msg, to=None):
        """Send a skill request from this actor"""

        cls = msg.__class__
        if not cls.__registered__:
            raise Exception(cls.__name__ + ' skill request not registered in any actor')
        subj = cls.__subject__
        act = cls.__action__
        body = dict(msg.__dict__)
        uid = str(uuid.uuid4())
        body['_uid'] = uid
        if to is not None:
            if '@' not in to:
                to = to + '@*'
            body['_target'] = to
        pending_requests[uid] = RequestInstance(cls.__response__)
        actor = self.__actor_name__()
        name = event_api_name(SEND_EVENT, actor, subj, act)
        post_event(prj_name, actor, name, body)
        return pending_requests[uid].fut

    def send_broadcast(self, msg):
        """Send a broadcast message from this actor"""

        cls = msg.__class__
        subj = cls.__subject__
        act = cls.__action__
        body = dict(msg.__dict__)
        uid = str(uuid.uuid4())
        body['_uid'] = uid
        actor = self.__actor_name__()
        name = event_api_name(SEND_EVENT, actor, subj, act)
        post_event(prj_name, actor, name, body)

class RequestInstance:
    def __init__(self, resp_cls):
        self.resp_cls = resp_cls
        self.fut = asyncio.get_running_loop().create_future()

    def set_response(self, obj):
        if self.resp_cls:
            data = import_paraflow_object(obj, self.resp_cls)
            self.fut.set_result(data)
        else:
            self.fut.set_result(None)



#################### Builder functions

#### custom types

graphql_typedefs = {}

def make_response_field(Query, field, gql_name):
    name = response_query_name(gql_name)
    resp_cls = field.__skill__.response
    @strawberry.type
    class Exemplar:
        @strawberry.field(name=name)
        def resolver(cid: str) -> resp_cls:
            return lookup_skill_response(cid)

    fields = [f for f in dataclasses.fields(Exemplar) if isinstance(f, StrawberryField)]
    field = fields[0]
    Query.__annotations__[name] = Exemplar.__annotations__['resolver']
    Query.__dataclass_fields__[name] = field
    Query.__strawberry_definition__.fields.append(field)


# Generate a resolver for a single actor class.
# If it has a conversation parameter a wrapper is created to convert
# the string parameter into a Conversation object.

def generate_single_resolver(cls, field, inst):
    conv_param = None
    for i in range(len(field.arguments)):
        if field.arguments[i].type == Conversation:
            args = list(field.arguments)
            conv = args[i]
            args[i] = StrawberryArgument(conv.python_name, '_cid', StrawberryAnnotation(str))
            field.arguments = args
            conv_param = conv.python_name

    callback = getattr(inst, field.name).__get__(inst, cls)
    if conv_param is not None:
        actor = inst.__actor_name__()
        subject = get_subject(cls, field)
        action = get_action(field)
        event = event_api_name('completed', actor, subject, action)

        @functools.wraps(getattr(cls, field.name))
        def resolver(*args,**kwargs):
            kwargs[conv_param] = Conversation(actor, event, kwargs[conv_param])
            return callback(**kwargs)
        return resolver
    else:
        return callback

# Generate a shared resolver for multiple actors
# These result from multiple actors implemented by the same class.
# The functools.wraps decoration enables the wrapper to look like it has the signature
# of the original method instead of the actual signature (**kwargs)

def generate_dispatch_resolver(cls, field, inst_list):
    conv_param = None
    for i in range(len(field.arguments)):
        if field.arguments[i].type == Conversation:
            args = list(field.arguments)
            conv = args[i]
            args[i] = StrawberryArgument(conv.python_name, '_cid', StrawberryAnnotation(str))
            field.arguments = args
            conv_param = conv.python_name

    # add extra arg to capture the target actor name
    actor_arg = StrawberryArgument('_actor', '_actor', StrawberryAnnotation(str))
    field.arguments.append(actor_arg)

    callbacks = {
        a.__actor_name__(): getattr(a, field.name).__get__(a, cls) for a in inst_list
    }

    if conv_param is not None:
        subject = get_subject(cls, field)
        action = get_action(field)

        @functools.wraps(getattr(cls, field.name))
        def resolver(*args,**kwargs):
            actor = kwargs['_actor']
            del kwargs['_actor']
            if actor in callbacks:
                event = event_api_name('completed', actor, subject, action)
                kwargs[conv_param] = Conversation(actor, event, kwargs[conv_param])
                return callbacks[actor](**kwargs)
            else:
                raise Exception('Invalid _actor ' + actor)
        return resolver
    else:
        @functools.wraps(getattr(cls, field.name))
        def resolver(*args,**kwargs):
            actor = kwargs['_actor']
            del kwargs['_actor']
            if actor in callbacks:
                return callbacks[actor](**kwargs)
            else:
                raise Exception('Invalid _actor ' + actor)
        return resolver

@strawberry.type
class SdkInfo:
    name: str
    version: str

def build_query():
    name_converter = gql_config.name_converter
    actors = list(actor_registry.values())

    @strawberry.type
    class Query:
        @strawberry.field
        def sdkVersion() -> SdkInfo:
            return SdkInfo(name='python',version=__version__)

        @strawberry.field
        def getActorMetadata() -> list[Actor]:
            return actors

    @strawberry.type
    class Mutation:
        @strawberry.field
        def skillRequestResponse(uid: str, response: strawberry.scalars.JSON) -> None:
            handle_skill_response(uid, response)

    for cls_name in actor_instances:
        inst_list = actor_instances[cls_name]
        inst = inst_list[0]
        cls = inst_list[0].__class__
        fields = [f for f in dataclasses.fields(cls) if isinstance(f, StrawberryField)]
        for field0 in fields:
            # need to copy because make_response_field modifies the field
            field = copy.copy(field0)
            field.__skill__ = field0.__skill__

            if field.__skill__.response and inspect.isclass(field.__skill__.response):
                make_response_field(Query, field, name_converter.from_field(field))

            if field.__skill__.response and not inspect.isclass(field.__skill__.response):
                # replace resolver
                field = field(getattr(inst,field.name).__get__(inst, cls))

                Query.__annotations__[field.name] = cls.__annotations__[field.name]
                Query.__dataclass_fields__[field.name] = field
                Query.__strawberry_definition__.fields.append(field)
            else:
                if len(inst_list) == 1:
                    field = field(generate_single_resolver(cls, field, inst_list[0]))
                else:
                    field = field(generate_dispatch_resolver(cls, field, inst_list))
                Mutation.__annotations__[field.name] = cls.__annotations__[field.name]
                Mutation.__dataclass_fields__[field.name] = field
                Mutation.__strawberry_definition__.fields.append(field)

    return Query,Mutation

def register_actor(actor, requests=[], broadcast=[], status=[]):
    """Registers an actor for deployment.
    
    - `actor` Instances of an actor class (i.e. class decorated with actor.actor).
    - `requests` List of skill request classes (i.e. classes decorated with actor.type) that define all the skill requests
       this actor makes.
    - `broadcast` List of broadcast classes (i.e. classes decorated with actor.type) that define all the messages this
       actor broadcasts.
    """

    a_cls = actor.__class__
    if not dataclasses.is_dataclass(a_cls):
        raise Exception('ERROR %s is missing @actor.actor class decorator' % (a_cls.__name__,))
    actor_name = actor.__actor_name__()

    actor_registry[actor_name] = build_actor(actor, requests, broadcast, status)
    if a_cls.__name__ in actor_instances:
        actor_instances[a_cls.__name__].append(actor)
    else:
        actor_instances[a_cls.__name__] = [actor]

def start_actors(prj, server, restart=True):
    return asyncio.ensure_future(launch_actors(prj,list(actor_registry.keys()), server.port, restart))

def _schema_test():
    q,m=build_query()
    schema=strawberry.Schema(query=q,mutation=m)
    print(schema)

    server = Server.get_instance()
    server.set_graphql_view(GraphQLView(schema=schema))

def deploy(prj, restart=True):
    """Deploy all registered actors.

       - `prj` Name of the created docker compose project.
       - `restart` Restart existing containers if already running.


       If running directly on the host, this function will start a docker compose project with one container per
       actor which communicates with the Python actors via the connector service.  In this case, the function
       will return an awaitable that returns when the deploy is complete.
    """

    global prj_name, graphql_typedefs

    graphql_typedefs = {}
    prj_name = prj

    q,m=build_query()
    schema=strawberry.Schema(query=q, mutation=m, config=gql_config)
    #print(schema)

    server = Server.get_instance()
    server.set_graphql_view(GraphQLView(schema=schema))

    if not use_external_paraflow():
        return start_actors(prj, server, restart)

__all__ = ['Conversation', 'BaseActor', 'actor', 'skill', 'type', 'observation', 'skill_request', 'register_actor', 'deploy']