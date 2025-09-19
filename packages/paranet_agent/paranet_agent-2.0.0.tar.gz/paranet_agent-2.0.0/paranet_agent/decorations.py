def get_subject(cls, field):
    return field.__skill__.subject or cls.__subject__

def get_action(field):
    return field.__skill__.action or field.name
