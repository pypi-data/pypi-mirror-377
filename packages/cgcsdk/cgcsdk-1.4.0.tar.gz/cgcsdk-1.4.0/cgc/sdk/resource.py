import json as _json
import cgc.sdk.exceptions as _exceptions
from cgc.commands.exceptions import NonOnPremisesException as _NonOnPremisesException
from cgc.utils.custom_exceptions import CUSTOM_EXCEPTIONS
import cgc.utils.prepare_headers as _prepare_headers
import cgc.commands.compute.compute_utils as _compute_utils
import cgc.utils.requests_helper as _requests_helper
import cgc.utils.response_utils as _response_utils
from enum import Enum as _Enum
from cgc.commands.compute.compute_models import GPUsList, ComputesList
from cgc.commands.db.db_models import DatabasesList
import warnings as _warnings


def start_function_loop(function, infinite: bool = True, *args, **kwargs):
    """
    Starts a function in a loop until it gets response code 200.

    Args:
        function: The function to be executed.
        infinite: A boolean indicating whether the loop should be infinite (default: True).
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Raises:
        _SDKException: If the response code is not 200 after 5 attempts (if finite) or if the response code is 409.

    Returns:
        None
    """
    import logging

    counter = 0
    while True:
        try:
            counter += 1
            response = function(*args, **kwargs)

            if type(response) is bool:
                if response:
                    break
            elif type(response) is dict:
                if response["code"] == 409:
                    raise _exceptions.SDKException(409, response)
                return response
        except _exceptions.SDKException as e:
            if e.code == 409:
                logging.warning(e)
                return
            logging.error(e)
        finally:
            if not infinite and counter > 4:
                raise _exceptions.SDKException(
                    -1, "Response code not 200 after 5 attempts."
                )


def stop_function_loop(function, infinite: bool = True, *args, **kwargs):
    """
    Stop function loop, proceed on response code 200.

    Args:
        function: The function to be stopped.
        infinite (bool): Flag indicating whether the loop should run infinitely or not.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.

    Raises:
        _SDKException: If the response code is not 200 after 5 attempts (if finite) or if the response code is 404.

    Returns:
        None
    """
    import logging

    counter = 0
    while True:
        try:
            counter += 1
            response = function(*args, **kwargs)
            if type(response) is bool:
                if not response:
                    break
            elif type(response) is dict:
                if response["code"] == 404:
                    raise _exceptions.SDKException(404, response)
                return response
        except _exceptions.SDKException as e:
            if e.code == 404:
                logging.warning(e)
                return
            logging.error(e)
        finally:
            if not infinite and counter > 4:
                raise _exceptions.SDKException(
                    -1, "Response code not 200 after 5 attempts."
                )


def compute_list():
    """
    List all compute apps for user namespace.
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type=compute"
    metric = "compute.list"
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.get,
        url=url,
        headers=headers,
    )
    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


class ResourceTypes(_Enum):
    compute = "compute"
    db = "db"
    job = "job"


def _resource_status_ready(name: str, response: dict):
    """
    Check if a resource is ready.

    Args:
        name: The name of the resource.
        response: The response from the API call.

    Returns:
        The response from the API call.
    """
    for pod in response["details"]["pods_list"]:
        try:
            if pod["labels"]["app-name"] == name:
                return pod["status"] == "Running"
        except KeyError:
            return False
    return False


def resource_ready(
    name: str, resource_type: ResourceTypes = ResourceTypes.compute
) -> bool:
    """
    Check if a resource is ready.

    Args:
        name: The name of the resource.
        resource_type: The type of resource to check (default: ResourceTypes.compute).

    Returns:
        bool: A boolean indicating whether the resource is ready.
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type={resource_type.value}"
    metric = "resource.list"
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.get,
        url=url,
        headers=headers,
    )
    validated_response = (
        _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
            __res, metric
        )
    )
    return _resource_status_ready(name, validated_response)


def db_list():
    """
    List all db apps for user namespace.
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list?resource_type=db"
    metric = "compute.list"
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.get,
        url=url,
        headers=headers,
    )
    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def get_entity_list() -> list[str]:
    """Get a list of all available entities for the enabled context.

    Returns:
        list: A list of entity names.
    """
    compute_models = ComputesList.load_data()
    database_models = DatabasesList.load_data()
    return compute_models + database_models


def compute_create_custom(
    name: str,
    image_name: str,
    cpu: int = 1,
    memory: int = 2,
    shm_size: int = 0,
    gpu: int = 0,
    gpu_type: str = "A5000",
    volumes: list = [],
    volume_full_path: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    resource_data: list = [],
    config_maps_data: list = [],
    node_port_enabled: bool = False,
):
    """Create a custom compute resource.

    Args:
        name (str): Name of the compute resource.
        image_name (str): Name of the image to use for the compute resource.
        cpu (int, optional): Number of CPUs for the compute resource. Defaults to 1.
        memory (int, optional): Amount of memory (in GB) for the compute resource. Defaults to 2.
        shm_size (int, optional): Size of the shared memory (in GB) for the compute resource. Defaults to 0.
        gpu (int, optional): Number of GPUs for the compute resource. Defaults to 0.
        gpu_type (str, optional): Type of GPU for the compute resource. Defaults to "A5000".
        volumes (list, optional): List of volumes to attach to the compute resource. Defaults to [].
        volume_full_path (str, optional): Full path of the volume. Defaults to "".
        startup_command (str, optional): Startup command for the compute resource. Defaults to "".
        repository_secret (str, optional): Secret for accessing the repository. Defaults to "".
        cgc_data (list[str], optional): Additional CGC data. Defaults to [].
        environment_data (list[str], optional): Additional environment data. Defaults to [].
        arguments_data (list[str], optional): Additional arguments data. Defaults to [].
        config_maps_data (list, optional): Additional config maps data. Defaults to [].
        node_port_enabled (bool, optional): A flag indicating whether the node port is enabled. Defaults to False.
    """

    if resource_data:
        raise _exceptions.SDKException(
            -1,
            "Resource data is not supported for resource creation anymore. Use new function `resource_create` instead.",
        )
    else:
        _warnings.warn(
            "compute_create_custom() is deprecated and will be removed in a future releases. Use resource_create() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    resource_create(
        name=name,
        image_name=image_name,
        entity="custom",
        cpu=cpu,
        memory=memory,
        shm_size=shm_size,
        gpu=gpu,
        gpu_type=gpu_type,
        volumes=volumes,
        volume_full_path=volume_full_path,
        startup_command=startup_command,
        repository_secret=repository_secret,
        cgc_data=[],
        environment_data=[],
        arguments_data=[],
        config_maps_data=config_maps_data,
        node_port_enabled=node_port_enabled,
    )


def resource_create(
    name: str,
    image_name: str,
    entity: str = "custom",
    cpu: int = 1,
    memory: int = 2,
    shm_size: int = 0,
    gpu: int = 0,
    gpu_type: str = "A5000",
    volumes: list = [],
    volume_full_path: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    cgc_data: list[str] = [],
    environment_data: list[str] = [],
    arguments_data: list[str] = [],
    config_maps_data: list = [],
    node_port_enabled: bool = False,
):
    """
    Create a compute or database resource.

    :param name: The name of the compute resource.
    :type name: str
    :param image_name: The name of the image to use for the compute resource.
    :type image_name: str,
    :param entity: The entity type for the compute resource, defaults to "custom".
    :type entity: str, optional
    :param cpu: The number of CPUs for the compute resource, defaults to 1.
    :type cpu: int, optional
    :param memory: The amount of memory (in GB) for the compute resource, defaults to 2.
    :type memory: int, optional
    :param shm_size: The size of the shared memory (in GB) for the compute resource, defaults to 0.
    :type shm_size: int, optional
    :param gpu: The number of GPUs for the compute resource, defaults to 0.
    :type gpu: int, optional
    :param gpu_type: The type of GPU for the compute resource, defaults to "A5000".
    :type gpu_type: str, optional
    :param volumes: The list of volumes to attach to the compute resource, defaults to [].
    :type volumes: list, optional
    :param volume_full_path: The full path of the volume, defaults to "".
    :type volume_full_path: str, optional
    :param startup_command: The startup command for the compute resource, defaults to "".
    :type startup_command: str, optional
    :param repository_secret: The secret for accessing the repository, defaults to "".
    :type repository_secret: str, optional
    :param cgc_data: The additional CGC data, defaults to [].
    :type cgc_data: list[str], optional
    :param environment_data: The additional environment data, defaults to [].
    :type environment_data: list[str], optional
    :param arguments_data: The additional arguments data, defaults to [].
    :type arguments_data: list[str], optional
    :param config_maps_data: The additional config maps data, defaults to [].
    :type config_maps_data: list, optional
    :param node_port_enabled: A flag indicating whether the node port is enabled, defaults to False.
    :type node_port_enabled: bool, optional
    :raises _SDKException: If the image name is not provided.
    :raises _SDKException: If an invalid GPU type is specified.
    :return: The response from the API call.
    :rtype: _type_
    """
    if not image_name:
        raise _exceptions.SDKException(-2, "Image name is required")
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/create"
    metric = "compute.create"
    gpu_type = gpu_type.upper()
    if gpu_type not in GPUsList.get_list():
        raise _exceptions.SDKException(-3, f"Invalid GPU type: {gpu_type}")
    try:
        __payload = _compute_utils.compute_create_payload(
            name=name,
            entity=entity,
            cpu=cpu,
            memory=memory,
            gpu=gpu,
            gpu_type=gpu_type,
            volumes=volumes,
            volume_full_path=volume_full_path,
            cgc_data=cgc_data,
            environment_data=environment_data,
            arguments_data=arguments_data,
            config_maps_data=config_maps_data,
            shm_size=shm_size,
            image_name=image_name,
            startup_command=startup_command,
            repository_secret=repository_secret,
            node_port_enabled=node_port_enabled,
        )
    except _NonOnPremisesException as err:
        raise _exceptions.SDKException(400, err) from err

    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.post,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def resource_update_port(
    name: str, port_name: str, new_port: int, ingress: bool = True
):
    """
    Update a port for an app using backend endpoint.

    :param name: name of app to edit
    :type name: str
    :param port_name: name of port to edit
    :type port_name: str
    :param new_port: new port number
    :type new_port: int
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=UPDATE"
    metric = "resource.ports.update"
    __payload = _compute_utils.port_modification_payload(
        port_name=port_name,
        port_number=new_port,
        ingress=ingress,
        app_name=name,
    )
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.post,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def resource_add_port(name: str, port_name: str, new_port: int, ingress: bool = True):
    """
    Add a port for an app using backend endpoint.

    :param name: name of app to edit
    :type name: str
    :param port_name: name of port to add
    :type port_name: str
    :param new_port: new port number
    :type new_port: int
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=ADD"
    metric = "resource.ports.add"
    __payload = _compute_utils.port_modification_payload(
        port_name=port_name,
        port_number=new_port,
        ingress=ingress,
        app_name=name,
    )
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.post,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def resource_delete_port(
    name: str,
    port_name: str,
):
    """
    Add a port for an app using backend endpoint.

    :param name: name of app to edit
    :type name: str
    :param port_name: name of port to delete
    :type port_name: str
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?port_modification_mode=DELETE"
    metric = "resource.ports.delete"
    __payload = _compute_utils.port_delete_payload(
        port_name=port_name,
        app_name=name,
    )
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.post,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def resource_list_ports(name: str):
    """
    List ports for an app using backend endpoint.

    :param name: name of app to list ports for
    :type name: str
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ports?resource_name={name}"
    metric = "resource.ports.list"
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.get,
        url=url,
        headers=headers,
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def resource_delete(name: str):
    """
    Delete an app using backend endpoint.

    :param name: name of app to delete
    :type name: str
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/delete"
    metric = "resource.delete"
    __payload = _compute_utils.compute_delete_payload(name=name)
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.delete,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )
