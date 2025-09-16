import json
import sys
from typing import List
from cgc.commands.cgc_helpers import parse_and_clean_command_input
from cgc.commands.exceptions import NonOnPremisesException
from cgc.utils.message_utils import prepare_warning_message
import click

from cgc.commands.compute.compute_models import ComputesList, GPUsList
from cgc.commands.compute.compute_responses import (
    compute_create_filebrowser_response,
    compute_create_response,
    compute_list_mounts_response,
    compute_list_response,
    get_compute_port_list,
)
from cgc.commands.compute.compute_utils import (
    compute_create_payload,
    port_delete_payload,
    port_modification_payload,
)
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    retrieve_and_validate_response_send_metric,
    tabulate_a_response,
)
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes
from cgc.commands.resource.resource_cmd import resource_delete


@click.group(name="compute", cls=CustomGroup)
def compute_group():
    """
    Management of compute resources.
    """


@compute_group.group(name="port", cls=CustomGroup)
def port_group():
    """
    Management of port resources.
    """


@click.group(name="filebrowser", cls=CustomGroup)
def filebrowser_group():
    """
    Management of filebrowser.
    """


@filebrowser_group.command("create", cls=CustomCommand)
@click.option("-u", "--puid", "puid", type=click.INT, required=False, default=0)
@click.option("-g", "--pgid", "pgid", type=click.INT, required=False, default=0)
def compute_filebrowser_create(puid: int, pgid: int):
    """Create a filebrowser service"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/filebrowser_create"
    metric = "compute.create_filebrowser"
    __payload = {"puid": puid, "pgid": pgid}
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_create_filebrowser_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@filebrowser_group.command("delete", cls=CustomCommand)
def compute_filebrowser_delete():
    """Delete a filebrowser service"""
    resource_delete("filebrowser")


@port_group.command("add", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
@click.option("-p", "--port", "port", type=click.INT, required=True, help="Port number")
@click.option(
    "-n",
    "--name",
    "port_name",
    type=click.STRING,
    required=True,
    help="Name of port",
)
@click.option(
    "-ni",
    "--no-ingress",
    "ingress",
    is_flag=True,
    type=click.BOOL,
    required=False,
    default=True,
    help="If set, port will NOT be exposed to the internet. By default port is exposed to the internet.",
)
@click.option(
    "-y",
    "--yes",
    "yes",
    is_flag=True,
    type=click.BOOL,
    required=False,
    default=False,
    help="If set, command will not ask for confirmation",
)
def compute_port_add(
    app_name: str, port_name: str, port: int, ingress: bool, yes: bool
):
    """Add a port to a running resource"""
    while True and not yes:
        click.echo(
            'Adding a port to a running resource will expose it to the internet. If you want to add a port without exposing it to the internet, use the "--no-ingress" flag.'
        )
        click.echo("Resource will be restarted after port addition.")
        answer = input("Do you want to continue? (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            sys.exit()
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=ADD"
    metric = "resource.ports.add"
    __payload = port_modification_payload(
        port_name=port_name,
        port_number=port,
        ingress=ingress,
        app_name=app_name,
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )

    __res_list = get_compute_port_list(
        retrieve_and_validate_response_send_metric(__res, metric)
    )
    table = fill_missing_values_in_a_response(__res_list)
    click.echo(f"Port {port_name} added successfully to {app_name}. Printing ports:")
    click.echo(tabulate_a_response(table))


@port_group.command("update", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
@click.option(
    "-p",
    "--port",
    "port",
    type=click.INT,
    required=False,
    help="Port number",
    default=None,
)
@click.option(
    "-n",
    "--name",
    "port_name",
    type=click.STRING,
    required=True,
    help="Name of port",
)
@click.option(
    "-ni",
    "--no-ingress",
    "ingress",
    is_flag=True,
    type=click.BOOL,
    required=False,
    default=True,
    help="If set, port will NOT be exposed to the internet. By default port is exposed to the internet.",
)
@click.option(
    "-y",
    "--yes",
    "yes",
    is_flag=True,
    type=click.BOOL,
    required=False,
    default=False,
    help="If set, command will not ask for confirmation",
)
def compute_port_update(
    app_name: str, port_name: str, port: int, ingress: bool, yes: bool
):
    """Update a port in a running resource"""
    while True and not yes:
        click.echo(
            'Updating a port in a running resource will expose it to the internet. If you want to update a port without exposing it to the internet, use the "--no-ingress" flag.'
        )
        click.echo("Resource will be restarted after port update.")
        answer = input("Do you want to continue? (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            sys.exit()
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=UPDATE"
    metric = "resource.ports.update"
    __payload = port_modification_payload(
        port_name=port_name,
        port_number=port,
        ingress=ingress,
        app_name=app_name,
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )

    retrieve_and_validate_response_send_metric(__res, metric)

    click.echo(f"Port {port_name} updated successfully in {app_name}")


@port_group.command("delete", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
@click.option(
    "-n",
    "--name",
    "port_name",
    type=click.STRING,
    required=True,
    help="Name of port",
)
@click.option(
    "-y",
    "--yes",
    "yes",
    is_flag=True,
    type=click.BOOL,
    required=False,
    default=False,
    help="If set, command will not ask for confirmation",
)
def compute_port_delete(app_name: str, port_name: str, yes: bool):
    """Delete a port from a running resource"""
    while True and not yes:
        click.echo(
            'Deleting a port from a running resource will expose it to the internet. If you want to delete a port without exposing it to the internet, use the "--no-ingress" flag.'
        )
        click.echo("Resource will be restarted after port delete.")
        answer = input("Do you want to continue? (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            sys.exit()
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=DELETE"
    metric = "resource.ports.delete"
    __payload = port_delete_payload(
        port_name=port_name,
        app_name=app_name,
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )

    retrieve_and_validate_response_send_metric(__res, metric)

    click.echo(f"Port {port_name} deleted successfully from {app_name}")


@port_group.command("list", cls=CustomCommand)
@click.argument(
    "app_name",
    type=click.STRING,
)
def compute_port_list(app_name: str):
    """List all ports for a running resource"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?resource_name={app_name}"
    metric = "resource.ports.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    __res_list = get_compute_port_list(
        retrieve_and_validate_response_send_metric(__res, metric)
    )
    table = fill_missing_values_in_a_response(__res_list)
    click.echo(tabulate_a_response(table))


@compute_group.command("create", cls=CustomCommand)
@click.argument("entity", type=click.Choice(ComputesList.get_list()))
@click.argument("arguments_data", required=False, nargs=-1)
@click.option(
    "-n", "--name", "name", type=click.STRING, required=True, help="Desired app name"
)
@click.option(
    "-g",
    "--gpu",
    "gpu",
    type=click.INT,
    default=0,
    help="How much GPU cards app will use",
)
@click.option(
    "-gt",
    "--gpu-type",
    "gpu_type",
    type=click.Choice(GPUsList.get_list(), case_sensitive=False),
    default="A5000",
    help="Graphic card used by the app",
)
@click.option(
    "-c",
    "--cpu",
    "cpu",
    type=click.INT,
    default=1,
    help="How much CPU cores app can use",
)
@click.option(
    "-m",
    "--memory",
    "memory",
    type=click.INT,
    default=2,
    help="How much Gi RAM app can use",
)
@click.option(
    "-v",
    "--volume",
    "volumes",
    multiple=True,
    help="List of volume names to be mounted with default mount path",
)
@click.option(
    "-fp",
    "--full-path",
    "volume_full_path",
    type=click.STRING,
    help="If set, full path will be used for volume mount. Valid for 1 volume.",
)
@click.option(
    "-ce",
    "--cgc-env",
    "cgc_data",
    multiple=True,
    help="List of optional CGC specific data to be passed to the app, key=value format",
)
@click.option(
    "-e",
    "--environment",
    "environment_data",
    multiple=True,
    help="List of optional environmental data to be passed to the app, key=value format; key= removes default value for the key",
)
@click.option(
    "--image",
    "image_name",
    type=click.STRING,
    help="Image to be used by the app",
)
@click.option(
    "--repository-secret",
    "repository_secret",
    type=click.STRING,
    help="Use secret to pull image from private repository",
)
@click.option(
    "-cm",
    "--config-map",
    "config_maps_data",
    multiple=True,
    help="List of optional arguments to be passed to the app, key=value format",
)
@click.option(
    "--shm",
    "shm_size",
    type=click.IntRange(0, 1024, clamp=True),
    default=0,
    help="Size of shared memory in Gi",
)
@click.option(
    "--node-port-enabled",
    "node_port_enabled",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="If set, app will be exposed to the internet via compute node addresses",
)
@click.option(
    "--debug-mode",
    "debug_mode",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="If set, debug mode is enabled and payload will be printed",
    hidden=True,
)
def compute_create(
    entity: str,
    gpu: int,
    gpu_type: str,
    cpu: int,
    memory: int,
    volumes: list[str],
    volume_full_path: str,
    config_maps_data: list[str],
    name: str,
    shm_size: int,
    image_name: str,
    cgc_data: list[str],
    environment_data: list[str],
    arguments_data: tuple[str],
    repository_secret: str,
    node_port_enabled: bool,
    debug_mode: bool,
):
    """
    Create an app in user namespace.
    \f
    :param entity: name of entity to create
    :type entity: str
    :param gpu: number of gpus to be used by app
    :type gpu: int
    :param gpu_type: graphic card type used by the app
    :type gpu_type: str
    :param cpu: number of cores to be used by app
    :type cpu: int
    :param memory: GB of memory to be used by app
    :type memory: int
    :param volumes: list of volumes to mount
    :type volumes: list[str]
    :param volume_full_path: if set, full path will be used for volume mount
    :type volume_full_path: str
    :param config_maps_data: list of optional config map arguments to be passed to the app
    :type config_maps_data: list[str]
    :param name: name of app
    :type name: str
    :param shm_size: size of shared memory
    :type shm_size: int
    :param image_name: name of image to be used by the app
    :type image_name: str
    :param cgc_data: list of optional CGC specific data to be passed to the app
    :type cgc_data: list[str]
    :param environment_data: list of optional environmental data to be passed to the app
    :type environment_data: list[str]
    :param arguments_data: tuple of optional arguments to be passed to the app
    :type arguments_data: tuple[str]
    :param repository_secret: use secret to pull image from private repository
    :type repository_secret: str
    :param node_port_enabled: if set, app ports will be exposed to the network via node addresses
    :type node_port_enabled: bool
    :param debug_mode: if set, debug mode is enabled and payload will be printed
    :type debug_mode: bool
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/create"
    cleaned_data, args_data = parse_and_clean_command_input(
        arguments_data=arguments_data
    )
    metric = "compute.create"
    try:
        __payload = compute_create_payload(
            name=name,
            entity=entity,
            cpu=cpu,
            memory=memory,
            gpu=gpu,
            volumes=volumes,
            volume_full_path=volume_full_path,
            cgc_data=cgc_data,
            environment_data=environment_data,
            arguments_data=args_data,
            config_maps_data=config_maps_data,
            gpu_type=gpu_type,
            shm_size=shm_size,
            image_name=image_name,
            startup_command=cleaned_data,
            repository_secret=repository_secret,
            node_port_enabled=node_port_enabled,
        )
    except NonOnPremisesException as err:
        click.echo(prepare_warning_message(err))
        return
    if debug_mode:
        click.echo(click.style("=== DEBUG PAYLOAD ===", fg="yellow", bold=True))
        click.echo(json.dumps(__payload, indent=2))
        click.echo(click.style("=== END DEBUG ===", fg="yellow", bold=True))

    # Extra keys allowed for payload:
    # 1.
    # template_specific_data: TemplateSpecificData
    #   TemplateSpecificData -> resource_data: Dict[AcceptedKeysForTemplateSpecificData, Union[list, Dict[str, str]]]
    # --- example: ---
    #   "template_specific_data": {
    # "resource_data": {
    #     "envs": {
    #         "postgre_host": "postgresql",  # dynamic & static -> POSTGRES_HOST=xxx or POSTGRE_HOST=xxx
    #         "postgre_password": "password",
    #         "postgre_name": "db",
    #     },
    #     "args": [
    #         "--hello=world",  # --hello world
    #         "--foo",  # --foo
    #         "--bar",  # --bar
    #     ],
    #     "cgc": {
    #         "IMAGE_PULL_SECRET_NAME": "my-secret",  # if set, image will be pulled from private repository (only for "custom" app)
    #         "APP_TOKEN": "my-app-token",  # if set, app will be started with this token
    #         "CUSTOM_COMMAND": "my-custom-command",  # if set, "custom" app will be started with this command
    #         "CUSTOM_IMAGE": "my-custom-image",  # this is taken from the PIPELINE for that command
    #     },
    # }
    #   }
    # currently available for label-studio
    # 2.
    # config_maps_data: dict [dict [str, str]]]
    # NOTE: filebrowser creation is NOT ALLOWED via this endpoint
    # NOTE: only valid config map names will be proceed
    # NOTE: only str values are allowed, otherwise config map will not be created and app might not start
    # ex.: config_maps_data = {"filebrowser-permissions-config": {
    #     "puid": "123",
    #     "pgid": "456",
    # }}
    # How to update payload with custom values?
    # payload["template_specific_data"] = dict(...)
    # payload["config_maps_data"] = dict(...)
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    if debug_mode:
        click.echo(click.style("=== DEBUG RESPONSE ===", fg="yellow", bold=True))
        click.echo(json.dumps(__res.json(), indent=2))
        click.echo(click.style("=== END DEBUG ===", fg="yellow", bold=True))
    click.echo(
        compute_create_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@compute_group.command("delete", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
def compute_delete_cmd(app_name: str):
    """
    Delete an app from user namespace.
    \f
    :param app_name: name of app to delete
    :type app_name: str
    """
    resource_delete(app_name)


compute_group.add_command(filebrowser_group)


@compute_group.command("list", cls=CustomCommand)
@click.option(
    "-d", "--detailed", "detailed", type=click.BOOL, is_flag=True, default=False
)
@click.option(
    "--debug-mode",
    "debug_mode",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="If set, debug mode is enabled and payload will be printed",
    hidden=True,
)
def resource_list(detailed: bool, debug_mode: bool):
    """
    List all apps for user namespace.
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type=compute"
    metric = "compute.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    if debug_mode:
        click.echo(click.style("=== DEBUG RESPONSE ===", fg="yellow", bold=True))
        click.echo(json.dumps(__res.json(), indent=2))
        click.echo(click.style("=== END DEBUG ===", fg="yellow", bold=True))
    table = compute_list_response(
        detailed,
        retrieve_and_validate_response_send_metric(__res, metric),
    )

    click.echo(table)


@compute_group.command("list-mounts", cls=CustomCommand)
def compute_list_mounts():
    """
    List all apps for user namespace.
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type=compute"
    metric = "compute.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    table = compute_list_mounts_response(
        retrieve_and_validate_response_send_metric(__res, metric),
    )

    click.echo(table)
