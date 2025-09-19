from strawberry.schema.config import StrawberryConfig

gql_config = StrawberryConfig(auto_camel_case=False)

SEND_EVENT = 'send'
COMPLETE_EVENT = 'completed'

def is_camel(s):
    if '_' in s:
        return False
    return any(c.isupper() for c in s[1:])

def capital_camel(s):
    if is_camel(s):
        return s[0:1].upper() + s[1:]
    words = s.split('_')
    return ''.join([w.title() for w in words])

def event_api_name(event, actor, subject, action):
    return ''.join([actor, event.title(), capital_camel(subject), capital_camel(action)])

def response_query_name(gql_name):
    return 'get%sResponse' % (gql_name.title(),)
