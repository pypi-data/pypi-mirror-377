import yaml
import os

def assign(obj, other):
    obj.update(other)
    return obj

def generate_compose(prj, actors, server_port, paranet, network, broker, paraflow_image, filename):
    env_vars = {}
    broker_url = 'http://%s:3131' % broker
    spec = {
      'services': {
        # 'mysql': {
        #   'image': 'mysql:8',
        #   'environment': {
        #     'MYSQL_ROOT_PASSWORD': 'admin',
        #     'MYSQL_DATABASE': 'paraflow'
        #   },
        #   'networks': ['paranet'],
        #   'healthcheck': {
        #     'test': "/usr/bin/mysql --user=root --password=admin --execute \"SHOW DATABASES;\"",
        #     'interval': '5s',
        #     'timeout': '20s',
        #     'retries': 10
        #   }
        # },
      },
      'networks': {
        'paranet': {
          'name': network,
          'external': True
        }
      }
    };

    if 'PYTHON_SDK_PARAFLOW_IMAGE' in os.environ:
        paraflow_image = os.environ['PYTHON_SDK_PARAFLOW_IMAGE']
    for actor in actors:
        actor_id = actor + '@1.0.0'
        spec['services'][actor+'-paraflow'] = {
          'image': paraflow_image,
          'platform': 'linux/amd64',
          'environment': assign({
            'OMICRON_LOCAL': '1',
            'OMICRON_LOCAL_DYNAMODB': 'http://dynamodb:8000',
            'AWS_ACCESS_KEY_ID': 'x',
            'AWS_SECRET_ACCESS_KEY': 'x',
            'ACTOR_ENDPOINT': 'graphql:http://host.docker.internal:%d' % (server_port,),
            'PARAFLOW_BACKEND': 'sqlite',
            'PARAFLOW_PARANET_HOST': broker_url,
            'PARAFLOW_ACTOR_ID': actor,
            'PARAFLOW_PARANET_ACTOR_ID_OVERRIDE': actor_id,
            #'RUST_LOG': 'warn'
            'RUST_LOG': 'debug,hyper::proto=info,h2=info'
          }, env_vars),
          'command': [
            '/usr/local/bin/graphql-actor',
            '--actor', actor,
            '--debugger',
            '--register',
            '--register-base'
          ],
          # 'depends_on': {
          #   'mysql': {
          #     'condition': 'service_healthy'
          #   }
          # },
          'extra_hosts': ['host.docker.internal:host-gateway'],
          'ports': ['3030'],
          'restart': 'always',
          'networks': ['paranet'],
          'labels': [
                'ai.paranet.actor.actor_entity_id='+actor_id,
                'ai.paranet.name='+paranet]
        }

    outf = open(filename, 'wb')
    outf.write(bytes(yaml.dump(spec), encoding='utf-8'))
    outf.close()
