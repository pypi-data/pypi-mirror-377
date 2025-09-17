
"""
Main entrypoint for the r7-surcom-sdk
"""

# PYTHON_ARGCOMPLETE_OK

import logging

import argcomplete

from r7_surcom_sdk.cmds import ConfigCmd, ConnectorsCmd, DataCmd, TypesCmd, DevCmd
from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_argparse import (Args, SurcomSDKArgHelpFormatter,
                                            SurcomSDKArgumentParser)
from r7_surcom_sdk.lib.sdk_terminal_fonts import fmt, formats

# Setup logging
# TODO: Be able to config for log formatter with env var
LOG = logging.getLogger(constants.LOGGER_NAME)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())


def get_parsers():

    parser_root = SurcomSDKArgumentParser(
        prog=constants.PROGRAM_NAME,
        description=f"Python software development kit (SDK) for building integrations with {constants.PRODUCT_NAME}, "
        f"also known as the {fmt(constants.FULL_PROGRAM_NAME, f=formats.BOLD)}.",
        epilog="For support, visit: "
               f"{fmt(constants.SUPPORT_LINK, f=formats.UNDERLINE)}",
        formatter_class=SurcomSDKArgHelpFormatter
    )

    parser_root.usage = f"""
    $ {constants.PROGRAM_NAME} <command> ...
    $ {constants.PROGRAM_NAME} -v <command> ...
    $ {constants.PROGRAM_NAME} --version
    """

    # Add --verbose argument
    parser_root.add_argument(*Args.verbose.flag, **Args.verbose.kwargs)

    # Add --version argument
    parser_root.add_argument(Args.version.flag, **Args.version.kwargs)

    parser_commands = parser_root.add_subparsers(
        title=f"{fmt(constants.CMD_COMMANDS, f=formats.BOLD)}",
        metavar="",
        dest=constants.CMD_MAIN
    )

    return parser_root, parser_commands


def main():

    parser_root, parser_commands = get_parsers()

    config_cmd = ConfigCmd(parent_parser=parser_commands)
    connectors_cmd = ConnectorsCmd(parent_parser=parser_commands)
    types_cmd = TypesCmd(parent_parser=parser_commands)
    data_cmd = DataCmd(parent_parser=parser_commands)

    if sdk_helpers.is_dev_mode_enabled():
        dev_cmd = DevCmd(parent_parser=parser_commands)

    # Run this to enable tab completion
    argcomplete.autocomplete(parser_root)

    args = parser_root.parse_args()

    if args.version:
        sdk_helpers.print_version()
        exit(0)

    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        SurcomSDKException.debug_mode = True
        sdk_helpers.print_log_msg("Verbose logging enabled", logging.DEBUG, divider=True)
        LOG.debug(f"The location of the surcom config file is '{constants.PATH_SURCOM_CONFIG_FILE}'")

    if args.main == constants.CMD_CONNECTORS:
        connectors_cmd.run(args)

    elif args.main == constants.CMD_CONFIG:
        config_cmd.run(args)

    elif args.main == constants.CMD_TYPES:
        types_cmd.run(args)

    elif args.main == constants.CMD_DATA:
        data_cmd.run(args)

    elif sdk_helpers.is_dev_mode_enabled() and args.main == constants.CMD_DEV:
        sdk_helpers.print_log_msg("Developer Mode Enabled", logging.WARNING, divider=True)
        dev_cmd.run(args)

    else:
        parser_root.print_help()


if __name__ == "__main__":
    main()
