import typing
from typing import Optional, Union, get_type_hints
import inspect
import dataclasses

import strawberry
from strawberry.types.field import StrawberryField

from .gql import *
from .decorations import get_action, get_subject


#################### GraphQL actor metadata schema

@strawberry.type
class ScalarType:
    name: str

@strawberry.type
class ColumnType:
    name: str
    datatype: str
    optional: bool

@strawberry.type
class TableType:
    columns: list[ColumnType]

@strawberry.type
class SkillArg:
    name: str
    datatype: Union[ScalarType,TableType]
    optional: bool

@strawberry.type
class SkillType:
    subject: str
    action: str
    inputs: list[SkillArg]
    outputs: list[SkillArg]
    eventName: str

@strawberry.type
class MessageType:
    name: str
    inputs: list[SkillArg]
    eventName: str

@strawberry.type
class Skill:
    subject: str
    action: str
    mutation: str
    response: Optional[str]
    background: Optional[bool]
    observe: Optional[bool]
    skillset: Optional[str]
    eventName: str
    annotations: Optional[list[str]]

@strawberry.type
class Actor:
    name: str
    skills: list[Skill]
    requests: list[SkillType]
    broadcast: list[SkillType]
    statusMessages: list[MessageType]


#################### Builder functions

noneType = type(None)

def get_field_type(py_type):
    optional = False
    org = typing.get_origin(py_type)
    if org == Union:
        types = typing.get_args(py_type)
        non_null = [t for t in types if t != noneType]
        if len(types) == 2 and len(non_null) == 1:
            # optional type
            py_type = non_null[0]
            optional = True
        else:
            elements = [t.__name__ for t in types]
            raise Exception(f'Unexpected union of {elements}')
    elif org == list:
        py_type = typing.get_args(py_type)[0]
        hints = get_type_hints(py_type)
        if len(hints) == 0:
            raise Exception('Unsupported list element type: ' + py_type.__name__)
        columns = []
        for name in hints:
            col_type, col_opt = get_field_type(hints[name])
            if isinstance(col_type, ScalarType):
                columns.append(ColumnType(name=name, datatype=col_type.name, optional=col_opt))
            else:
                raise Exception('Unsupported column type in ' + py_type.__name__)
        return (TableType(columns=columns), optional)

    if py_type == int:
        datatype = 'int'
    elif py_type == float:
        datatype = 'double'
    elif py_type == str:
        datatype = 'string'
    elif dataclasses.is_dataclass(py_type):
        datatype = 'json'
    else:
        raise Exception(f'Unsupported type: {py_type.__name__}')
    return (ScalarType(name=datatype), optional)

# convert py type to Paraflow type
def build_arg(name, py_type):
    datatype, optional = get_field_type(py_type)
    return SkillArg(name=name,datatype=datatype,optional=optional)

def build_arg_list(cls):
    hints = get_type_hints(cls)
    args = []
    for name in hints:
        args.append(build_arg(name, hints[name]))
    return args

def build_request(actor_cls, actor_name, cls):
    if cls.__subject__ == None:
        # update this field so it can be used in send_request
        cls.__subject__ = actor_cls.__subject__
    subj = cls.__subject__
    act = cls.__action__
    inputs = build_arg_list(cls)
    response = cls.__response__
    if response:
        outputs = build_arg_list(response)
    else:
        outputs = []
    event = event_api_name(SEND_EVENT, actor_name, subj, act)
    cls.__registered__ = True
    return SkillType(subject=subj, action=act, inputs=inputs, outputs=outputs, eventName=event)

def build_broadcast(actor_cls, actor_name, cls):
    if cls.__subject__ == None:
        # update this field so it can be used in send_broadcast
        cls.__subject__ = actor_cls.__subject__
    subj = cls.__subject__
    act = cls.__action__
    inputs = build_arg_list(cls)
    cls.__registered__ = True
    event = event_api_name(SEND_EVENT, actor_name, subj, act)
    return SkillType(subject=subj, action=act, inputs=inputs, outputs=[], eventName=event)

def build_pncp_message(actor_name, cls):
    name = cls.__name__
    cls.__registered__ = True
    inputs = build_arg_list(cls)
    event = event_api_name(SEND_EVENT, actor_name, name, '')
    return MessageType(name=name, inputs=inputs, eventName=event)

def build_skills(cls, actor_name):
    name_converter = gql_config.name_converter
    fields = [f for f in dataclasses.fields(cls) if isinstance(f, StrawberryField)]
    responses = {}
    for field in fields:
        if field.__skill__.response:
            if inspect.isclass(field.__skill__.response):
                response = response_query_name(name_converter.from_field(field))
            else:
                response = name_converter.from_field(field)
            subj = get_subject(cls, field)
            if subj not in responses:
                responses[subj] = {}
            act = get_action(field)
            responses[subj][act] = response

    skills = []
    for field in fields:
        if not field.__skill__.response or inspect.isclass(field.__skill__.response):
            subj = get_subject(cls, field)
            act = get_action(field)
            bg = field.__skill__.bg
            observe = field.__skill__.observe
            has_response = False
            if subj in responses:
                has_response = act in responses[subj]
            if bg != None and bg:
                if not has_response:
                    print('WARNING: %s/%s completes without a response' % (subj, act))
            else:
                if has_response:
                    raise Exception('ERROR: %s/%s has response method but skill does not have background=True' % (subj,act))
            mutation = name_converter.from_field(field)
            response = None
            if subj in responses:
                if act in responses[subj]:
                    response = responses[subj][act]
            skillset = field.__skill__.skillset
            event = event_api_name(COMPLETE_EVENT, actor_name, subj, act)
            annotations = []
            if field.__skill__.instance_param != None:
                annotations.append(f"%actor_instance(param={field.__skill__.instance_param})")
            skill = Skill(subject=subj,action=act,mutation=mutation,response=response,background=bg,observe=observe,skillset=skillset,eventName=event,annotations=annotations)
            skills.append(skill)
    return skills

def build_actor(actor, requests, broadcast, status):
    cls = actor.__class__
    actor_name = actor.__actor_name__()
    skills = build_skills(cls, actor_name)
    requests = [build_request(cls, actor_name, cls) for cls in requests]
    broadcast = [build_broadcast(cls, actor_name, cls) for cls in broadcast]
    status = [build_pncp_message(actor_name, cls) for cls in status]
    return Actor(name=actor_name, skills=skills, requests=requests, broadcast=broadcast, statusMessages=status)