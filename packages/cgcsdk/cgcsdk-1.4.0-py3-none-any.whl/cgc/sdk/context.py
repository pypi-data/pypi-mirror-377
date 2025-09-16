from typing import List
import cgc.utils as _utils
import cgc.utils.config_utils as _config_utils
import cgc.sdk.exceptions as _exceptions
import logging as _logging

_logger = _logging.getLogger(__name__)


def switch_context(number: int):
    """Set which namespace config should be used. After switching context your next command will be run in given namespace that corresponds to user namespace

    :param number: Number of context to switch to
    :type number: int

    :raises SDKException: If the context does not exist, cannot be switched or if any other error occurs during the process.

    :return: None
    :rtype: None
    """
    file_name = f"{number}.json" if number > 1 else "cfg.json"
    try:
        if not _utils.check_if_config_exist(file_name):
            _logger.error("Selected context '%s' does not exist.", file_name)
            _logger.info("To get all available contexts use: cgc context list")
            raise _exceptions.SDKException(-1, f"Context {number} does not exist")
        _utils.set_environment_data("CONFIG_FILE_NAME", file_name)
        _config_utils.save_to_local_config_context(file_name)
    except _exceptions.SDKException:
        raise
    except Exception as e:
        raise _exceptions.SDKException(-1, f"Failed to switch context: {e}") from e


def list_contexts() -> List[str]:
    """List all available contexts

    Keep in mind that `switch` command requires NUMBER of context, not its name.

    :raises SDKException: If there is an error while listing contexts.

    :return: List of context names
    :rtype: List[str]
    """
    try:
        return _utils.list_all_config_files()
    except Exception as e:
        raise _exceptions.SDKException(-1, f"Failed to list contexts: {e}") from e
