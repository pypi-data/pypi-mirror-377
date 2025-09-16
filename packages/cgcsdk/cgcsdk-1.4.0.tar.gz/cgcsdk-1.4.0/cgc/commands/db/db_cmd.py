import json
from cgc.commands.cgc_helpers import parse_and_clean_command_input
from cgc.utils.message_utils import prepare_warning_message
import click

from cgc.commands.compute.compute_responses import compute_list_response
from cgc.commands.db.db_models import DatabasesList
from cgc.commands.compute.compute_responses import compute_create_response
from cgc.commands.compute.compute_utils import compute_create_payload
from cgc.commands.exceptions import DatabaseCreationException, NonOnPremisesException
from cgc.commands.resource.resource_cmd import resource_delete
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group(name="db", cls=CustomGroup)
def db_group():
    """
    Management of db resources.
    """


@db_group.command("create", cls=CustomCommand)
@click.argument("entity", type=click.Choice(DatabasesList.get_list()))
@click.argument("arguments_data", required=False, nargs=-1)
@click.option("-n", "--name", "name", type=click.STRING, required=True)
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
    help="Volume name to be mounted with default mount path",
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
def db_create(
    entity: str,
    cpu: int,
    memory: int,
    volumes: list[str],
    name: str,
    arguments_data: tuple[str] = (),
    cgc_data: list[str] = [],
    environment_data: list[str] = [],
):
    """
    Create an app in user namespace.
    \f
    :param entity: name of entity to create
    :type entity: str
    :param cpu: number of cores to be used by app
    :type cpu: int
    :param memory: GB of memory to be used by app
    :type memory: int
    :param volumes: list of volumes to mount
    :type volumes: list[str]
    :param name: name of app
    :type name: str
    """
    try:
        DatabasesList.verify(entity)
    except DatabaseCreationException as e:
        click.echo(e, err=True, color="yellow")
        return
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/create"
    cleaned_data, args_data = parse_and_clean_command_input(
        arguments_data=arguments_data
    )
    metric = "db.create"
    try:
        __payload = compute_create_payload(
            name=name,
            entity=entity,
            cpu=cpu,
            memory=memory,
            volumes=volumes,
            startup_command=cleaned_data,
            arguments_data=args_data,
            cgc_data=cgc_data,
            environment_data=environment_data,
        )
    except NonOnPremisesException as err:
        click.echo(prepare_warning_message(err))
        return
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_create_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@db_group.command("delete", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def db_delete_cmd(name: str):
    """
    Delete an app from user namespace.
    \f
    :param name: name of app to delete
    :type name: str
    """
    resource_delete(name)


@db_group.command("list", cls=CustomCommand)
@click.option(
    "-d", "--detailed", "detailed", type=click.BOOL, is_flag=True, default=False
)
def resource_list(detailed: bool):
    """
    List all apps for user namespace.
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type=db"
    metric = "db.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    table = compute_list_response(
        detailed,
        retrieve_and_validate_response_send_metric(__res, metric),
    )

    click.echo(table)
