import os

is_external = 'PARAFLOW_HOST' in os.environ
PARAFLOW_HOST = os.environ.get('PARAFLOW_HOST','http://localhost:3023')

def use_external_paraflow():
  return is_external

__all__ = ['PARAFLOW_HOST', 'use_external_paraflow']