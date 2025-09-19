# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import atexit
import socket
import docker
import json
import urllib.request
import tempfile
from pathlib import Path
from typing import Dict, Optional, Set
import tarfile
from io import BytesIO
from functools import lru_cache
from http import HTTPStatus
import base64

from docker.models.containers import Container
from docker.models.images import Image
from jupyter_server.serverapp import ServerApp

from .utils import maybe_await


class WebRTCManager:
    http_port = 8080
    report_path_to_container = {}
    image_name = 'nvidia/devtools/nsight-streamer-{}'
    timeout = 10     # seconds
    inside_docker = Path('/.dockerenv').exists()
    report_dir_path = Path('/mnt/host')

    # Default paths for SSL certificate and key files in selkies-gstreamer, used by Nsight Streamer.
    ssl_keyfile_path = Path('/etc/ssl/private/ssl-cert-snakeoil.key')
    ssl_certfile_path = Path('/etc/ssl/certs/ssl-cert-snakeoil.pem')
    # In https mode, we wrap the Nsight Streamer entrypoint script
    # to set the SELKIES_ENABLE_HTTPS environment variable.
    https_entrypoint_script_path = Path('/setup/entrypoint-https.sh')

    atexit.register(
        lambda: [container.stop() for container in WebRTCManager.report_path_to_container.values()])

    @classmethod
    def get_docker_client(cls):
        try:
            return docker.DockerClient()
        except docker.errors.DockerException as e:
            if cls.inside_docker:
                message = 'Failed to start docker client. Is the docker socket mounted? ' \
                    '(try adding "-v /var/run/docker.sock:/var/run/docker.sock" ' \
                    'to the docker run command).'
            else:
                message = 'Failed to start docker client. Is the docker service running? ' \
                    '(start it with "systemctl start docker").'

            message += ' Also make sure you have sufficient permissions, see: ' \
                'https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user'
            raise RuntimeError(message) from e

    @classmethod
    def get_docker_image(cls, docker_client: docker.DockerClient, tool_type: str):
        version = cls.get_latest_image_version(tool_type)
        image = f'nvcr.io/{cls.image_name.format(tool_type)}'
        return docker_client.images.get(f'{image}:{version}')

    @classmethod
    async def create_container(cls, tool_type: str, report_path: Path, host: str,
                               max_resolution: Optional[str], allowed_ports: Set[int]):
        client = cls.get_docker_client()
        image = cls.get_docker_image(client, tool_type)

        if cls.inside_docker:
            http_port, turn_port = cls._get_free_ports_for_container(client, image, allowed_ports)
        else:
            http_port, turn_port = cls._get_free_ports(allowed_ports)

        devtool_cmd = cls.get_image_env_var(image, 'DEVTOOL_CMD')
        ports = {cls.http_port: http_port, turn_port: turn_port}
        environment = {
            'DEVTOOL_CMD': f'{devtool_cmd} {cls.report_dir_path / report_path.name}',
            'HOST_IP': host,
            'TURN_PORT': str(turn_port),
            'WEB_USERNAME': '',
        }
        if max_resolution:
            environment['MAX_RESOLUTION'] = max_resolution

        server_app = ServerApp.instance()
        https_enabled = bool(server_app.certfile and server_app.keyfile)
        entrypoint = ['/bin/bash', str(cls.https_entrypoint_script_path)] if https_enabled else None

        container = client.containers.create(
            image=image,
            ports=ports,
            environment=environment,
            detach=True,
            auto_remove=True,
            entrypoint=entrypoint,
            # Note: Never use volumes= because it won't work when running inside a docker container.
        )

        await cls._copy_report_to_container(container, report_path, str(cls.report_dir_path))

        if https_enabled:
            cls._copy_to_container(container, Path(server_app.certfile),
                                   cls.ssl_certfile_path.parent, cls.ssl_certfile_path.name)
            cls._copy_to_container(container, Path(server_app.keyfile),
                                   cls.ssl_keyfile_path.parent, cls.ssl_keyfile_path.name)
            with tempfile.NamedTemporaryFile(mode='w') as tf:
                tf.write(f"""
    sudo su - "$USER" -c 'echo "export SELKIES_ENABLE_HTTPS=true" >> ~/.bashrc'
    chmod 755 {cls.ssl_keyfile_path.parent}
    chmod 755 {cls.ssl_keyfile_path}
    chmod 755 {cls.ssl_certfile_path}
    source /setup/entrypoint.sh "$@"
    """)
                tf.flush()
                cls._copy_to_container(container, Path(tf.name), cls.https_entrypoint_script_path.parent,
                                       cls.https_entrypoint_script_path.name)

        container.start()
        cls.report_path_to_container[report_path] = container

    @classmethod
    async def run(cls, tool_type: str, report_path: Path, host: str, max_resolution: Optional[str],
                  allowed_ports: Set[int]):
        if report_path not in cls.report_path_to_container:
            await cls.create_container(tool_type, report_path, host, max_resolution, allowed_ports)
        container = cls.report_path_to_container[report_path]
        return cls.get_docker_client().api.port(container.id, cls.http_port)[0]["HostPort"]

    @classmethod
    def stop(cls, report_path: Path):
        cls.report_path_to_container[report_path].stop()
        del cls.report_path_to_container[report_path]

    @staticmethod
    def _get_free_ports(allowed_ports: Set[int]):
        if not allowed_ports:
            # Allowed ports are not specified - use a random port for the turn port.
            # Returning http_port as None to leave docker to assign a port.
            with socket.socket() as s:
                s.bind(('', 0))
                return None, s.getsockname()[1]

        # Find the first free port in the allowed ports - this is the HTTP port.
        for port in allowed_ports:
            with socket.socket() as s:
                try:
                    s.bind(('', port))
                    http_port = port
                    break
                except OSError:
                    continue
        else:
            raise RuntimeError('All allowed ports are in use')

        # The turn port should be a free port that is NOT in the allowed ports.
        # To do so, we first bind all free ports in the allowed ports.
        # Then, binding to a random port (so the random port is not in the allowed ports).
        sockets = []
        try:
            for port in allowed_ports:
                s = socket.socket()
                try:
                    s.bind(('', port))
                    sockets.append(s)
                except OSError:
                    s.close()
            with socket.socket() as s:
                s.bind(('', 0))
                return http_port, s.getsockname()[1]
        finally:
            for s in sockets:
                s.close()

    @staticmethod
    def _get_free_ports_for_container(client: docker.DockerClient, image: Image,
                                      allowed_ports: Set[int]):
        """
        Get two free ports from the docker host (to be used as HTTP and TURN ports).
        This method is used when running inside a docker container.
        Since we can't get the host's ports directly, we start a container
        and let docker assign the ports. We then stop the container and return the ports,
        to be used when creating the actual container.
        """
        
        def create_dummy_container(ports: Dict[int, int]) -> Container:
            return client.containers.run(image=image, command='sleep infinity', detach=True,
                                         remove=True, stop_signal='SIGKILL', ports=ports)
        
        if allowed_ports:
            # The turn port should be a free port that is NOT in the allowed ports.
            for turn_port in range(1024, 65535):
                if turn_port not in allowed_ports:
                    break
            else:
                raise RuntimeError('Failed to get free ports for container, '
                                   'try reducing the number of allowed ports')

            # Find all free ports in the allowed ports.
            free_ports = []
            for port in allowed_ports:
                try:
                    container = create_dummy_container({port: port})
                    free_ports.append(port)
                    container.stop()
                except docker.errors.APIError as e:
                    if e.status_code == HTTPStatus.INTERNAL_SERVER_ERROR.value:
                        continue
                    raise RuntimeError('Failed to get free ports for container') from e
            if not free_ports:
                raise RuntimeError('All allowed ports are in use')

            # Use the first free port as the HTTP port.
            http_port = free_ports[0]
            # Let docker assign the turn port.
            # Binding all free ports to the dummy container will prevent docker from assigning
            # a port from the allowed ports to the turn port.
            container = create_dummy_container(
                {port: port for port in free_ports} | {turn_port: None})
            turn_port: int = client.api.port(container.id, turn_port)[0]["HostPort"]
            container.stop()
            return http_port, turn_port
        else:
            # Allowed ports are not specified - let docker assign the ports.
            http_port = WebRTCManager.http_port
            turn_port = WebRTCManager.http_port + 1
            container = create_dummy_container({http_port: None, turn_port: None})

            http_port: int = client.api.port(container.id, http_port)[0]["HostPort"]
            turn_port: int = client.api.port(container.id, turn_port)[0]["HostPort"]
            container.stop()
            return http_port, turn_port

    @staticmethod
    async def _copy_report_to_container(container: Container, report_path: Path, to: str):
        if report_path.is_absolute():
            # `normalize_path` returns absolute path only when the output directory setting
            # is set to an absolute path, that is not relative to the server root.
            # In this case, ContentsManager can't and should not be used.
            WebRTCManager._copy_to_container(container, report_path, to)
            return

        # For relative paths, ContentsManager MUST be used. Because the file system
        # is not guaranteed to be mounted locally.
        contents_manager = ServerApp.instance().contents_manager
        report_path_str = str(report_path)
        model = await maybe_await(contents_manager.get(report_path_str))
        content = base64.b64decode(model['content'])
        stream = BytesIO()
        with tarfile.open(fileobj=stream, mode='w|') as tar:
            file_info = tarfile.TarInfo(name=report_path.name)
            file_info.size = len(content)
            tar.addfile(file_info, BytesIO(content))

        container.put_archive(to, stream.getvalue())

    @staticmethod
    def _copy_to_container(container: Container, src: Path, to: str, arcname: Optional[str] = None):
        stream = BytesIO()
        with tarfile.open(fileobj=stream, mode='w|') as tar:
            tar.add(src, arcname=arcname or src.name)

        container.put_archive(to, stream.getvalue())

    @staticmethod
    def get_image_env_var(image: Image, env_var: str) -> str:
        return next(filter(lambda x: x.startswith(f'{env_var}='), image.attrs['Config']['Env'])
               ).split('=')[1]

    @classmethod
    @lru_cache(maxsize=None)
    def get_latest_image_version(cls, tool_type: str):
        with urllib.request.urlopen(
            f'https://api.ngc.nvidia.com/v2/repos/{cls.image_name.format(tool_type)}'
        ) as response:
            return json.loads(response.read().decode())['latestTag']

    @classmethod
    def pull_image(cls, tool_type: str):
        cls.get_docker_client().images.pull(
            f'nvcr.io/{cls.image_name.format(tool_type)}:'
            + cls.get_latest_image_version(tool_type))
