
from r7_surcom_sdk.cmds.dev.ext_lib_docs import ExtLibraryDocsCommand
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKMainCommand


class DevCmd(SurcomSDKMainCommand):

    """
    [help]
    Hidden Developer Commands
    ---

    [description]
    These commands are intended for internal use and testing only.
They are not supported for general use.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} ext-lib-docs
    ---
    """
    def __init__(self, parent_parser):

        cmd_docstr = self.__doc__.format(
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=constants.CMD_DEV
        )

        super().__init__(
            parent=parent_parser,
            cmd_name=constants.CMD_DEV,
            cmd_docstr=cmd_docstr
        )

        # Add sub commands
        self.cmd_ext_lib_docs = ExtLibraryDocsCommand(self.cmd_parser)

    def run(self, args):

        if args.dev == constants.CMD_EXT_LIBRARY_DOCS:
            self.cmd_ext_lib_docs.run(args)

        else:
            self.main_parser.print_help()
