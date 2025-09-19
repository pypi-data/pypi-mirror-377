import os
import asyncio
from python_on_whales import docker
from python_on_whales import DockerClient

from .composer import generate_compose

if 'LOCALAPPDATA' in os.environ:
    appdir = os.path.join(os.environ['LOCALAPPDATA'], 'paranet-python')
else:
    appdir = os.path.join(os.environ['HOME'], '.paranet-python')

if not os.path.isdir(appdir):
    os.mkdir(appdir)

def compose_filename(prj):
    folder = os.path.join(appdir, prj)
    if not os.path.isdir(folder):
        os.mkdir(folder)

    return os.path.join(folder, 'docker-compose.yml')

def start_project(filename):
    client = DockerClient(compose_files=[filename])
    client.compose.up(detach=True,wait=True)

def stop_project(filename):
    client = DockerClient(compose_files=[filename])
    client.compose.stop()

def get_node_detail():
    containers = docker.ps()
    projects = {}
    for x in containers:
        labels = x.config.labels
        if 'com.docker.compose.project' not in labels:
            continue

        project = labels['com.docker.compose.project']
        if project not in projects:
            projects[project] = {}

        if 'grokit' in x.config.image or 'otonoma' in x.config.image:
            #### Otonoma container

            nets = list(x.network_settings.networks.keys())
            if len(nets) == 1:
                projects[project]['net'] = nets[0]
                ports = list(x.network_settings.ports)
                if '3131/tcp' in ports:
                    # found broker
                    network = x.network_settings.networks[nets[0]]
                    projects[project]['broker'] = {'ip': network.ip_address}
            if labels.get('com.docker.compose.service') == 'net_debugger':
                image = x.config.image
                projects[project]['paraflow'] = {'image': image}

    for name in projects:
        prj = projects[name]
        if 'broker' in prj and 'net' in prj and 'paraflow' in prj:
            return {'project': name,
                    'net': prj['net'],
                    'broker-ip': prj['broker']['ip'],
                    'paraflow-image': prj['paraflow']['image']}
    return None

async def launch_actors(prj, actors, port, restart):
    loop = asyncio.get_running_loop()

    node_detail = await loop.run_in_executor(None, get_node_detail)
    if not node_detail:
        raise Exception('Failed to find Paranet docker-compose environment')

    print(node_detail)

    filename = compose_filename(prj)
    if os.path.isfile(filename):
        if restart:
            print('Stopping actors')
            await loop.run_in_executor(None, lambda: stop_project(filename))
            print('Restarting actors:', ','.join(actors))
        else:
            print('Skipping actors restart')
    else:
        print('Starting actors:', ','.join(actors))

    generate_compose(prj, actors, port, node_detail['project'], node_detail['net'], node_detail['broker-ip'], node_detail['paraflow-image'], filename)
    await loop.run_in_executor(None, lambda: start_project(filename))

    print('Actors running')
