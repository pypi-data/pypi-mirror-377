import sys
from typing import List
from cgc.utils import quick_sort
from cgc.utils.config_utils import get_config_file_name, read_from_cfg
from tabulate import tabulate


def _is_main_context_file(file: str) -> bool:
    if get_config_file_name() == file:
        return True
    return None


def table_of_user_context_files(config_files: List[str]):
    # print tabulate of: [context NR | namespace | user_id]
    headers = ["Context No.", "Namespace", "User ID", "URL", "Is active"]
    contexts = []
    contexts_nrs = []
    for file in config_files:
        file_context = []
        file_context.append(
            int(file.split(".")[0]) if file != "cfg.json" else 1
        )  # should never throw exception with good config_file list
        contexts_nrs.append(file_context[0])
        file_data = read_from_cfg(None, file)
        values_to_read = ["namespace", "user_id", "cgc_api_url"]
        for k in values_to_read:
            try:
                value = file_data[k]
            except KeyError:
                value = None
                if k == "cgc_api_url":
                    value = "https://cgc-api.comtegra.cloud:443"
            file_context.append(value)

        file_context.append(_is_main_context_file(file))
        contexts.append(file_context)

    contexts_nrs_sorted = quick_sort(contexts_nrs)
    contexts_sorted = []
    for context in contexts_nrs_sorted:
        contexts_sorted.append(contexts[contexts_nrs.index(context)])

    return tabulate(contexts_sorted, headers=headers)


def parse_and_clean_command_input(arguments_data):
    cleaned_data = ""
    if arguments_data:
        arguments_data_list = list(arguments_data)
    else:
        arguments_data_list = []
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
        cleaned_data = input_data.replace("|", "")
    if cleaned_data and cleaned_data == "--":
        cleaned_data = ""
    final_arguments_data = []
    if arguments_data_list:
        # if there is a "--key value", merge them into one string
        # e.g. ["--key", "value"] -> ["--key value"]
        for i in range(0, len(arguments_data_list), 2):
            if i + 1 < len(arguments_data_list):
                first_arg = arguments_data_list[i]
                second_arg = arguments_data_list[i + 1]

                # Ensure first argument has "--" and second doesn't
                if first_arg.startswith("--") and not second_arg.startswith("--"):
                    final_arguments_data.append(f"{first_arg} {second_arg}")
                elif first_arg.startswith("-") and not second_arg.startswith("-"):
                    final_arguments_data.append(f"{first_arg} {second_arg}")
                else:
                    # If pattern doesn't match, add them separately
                    final_arguments_data.append(first_arg)
                    final_arguments_data.append(second_arg)
            else:
                final_arguments_data.append(arguments_data_list[i])
    return cleaned_data, final_arguments_data
