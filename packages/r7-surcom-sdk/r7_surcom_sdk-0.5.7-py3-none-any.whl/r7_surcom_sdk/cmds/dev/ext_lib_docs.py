import logging
import os
import re
import shutil
import uuid
import datetime
import json

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class ExtLibraryDocsCommand(SurcomSDKSubCommand):
    """
    [help]
    Generate Rapid7 Extension Library documentation for a Connector
    ---

    [description]
    This command generates a Connector's documentation for the Rapid7 Extension Library.

    `--path-connector`\t should be an already packaged connector, with a manifest.yaml file.
    `--output`\t\t is the output directory where the docs will be generated
    `--dir-structure`\t is the directory structure to create in the output directory, e.g. rapid7/extensions/connector
    `--host-url`\t is the URL that is used to host the screenshots that are referenced within in the Markdown file
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_DEV
        self.sub_cmd_name = constants.CMD_EXT_LIBRARY_DOCS

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)

        self.cmd_parser.add_argument(
            *Args.dir_output.flag,
            dest="dir_output",
            help="The output directory",
            required=True
        )

        self.cmd_parser.add_argument(
            "--dir-structure",
            help="The directory structure to create the docs in",
            required=True
        )

        self.cmd_parser.add_argument(
            "--host-url",
            help="URL that is used to display the screenshots within Markdown",
            required=True
        )

    def _copy_logo(
        self,
        path_output: str,
        src_loc_logo: str,
        target_loc_logo: str
    ) -> str:
        """
        Get the icon from current location and copy to the r7 docs location
        and return the relative path to the logo

        :return: Relative path to the logo. Used in the generated manifest.json file
        :rtype: str
        """
        filename_and_ext = os.path.splitext(os.path.basename(src_loc_logo))

        logo_name = f"logo{filename_and_ext[1]}"

        rel_path_logo = os.path.join(os.path.relpath(path=target_loc_logo, start=path_output), logo_name)
        abs_path_logo = os.path.join(target_loc_logo, logo_name)

        if not os.path.isfile(abs_path_logo):
            sdk_helpers.print_log_msg(
                f"Copy logo from '{src_loc_logo}' to '{abs_path_logo}'"
            )
            shutil.copyfile(src=src_loc_logo, dst=abs_path_logo)

        return rel_path_logo

    def _handle_screenshots(
        self,
        path_output: str,
        src_loc_screenshots_dir: str,
        target_loc_screenshots_dir: str,
        instructions_body: str,
        screenshot_references: list,
        host_images_url: str
    ) -> tuple[str, list]:
        """
        Copy the contents of `src_loc_screenshots_dir` to `target_loc_screenshots_dir`

        Given the instructions, replace any screenshot references with the absolute URL

        :return: the modified instructions text and a list of all screenshots with relative paths,
            used in the manifest.json file
        :rtype: tuple[str, list]
        """
        sdk_helpers.print_log_msg(
            f"Copying contents of docs dir from '{src_loc_screenshots_dir}' to '{target_loc_screenshots_dir}'"
        )

        # List of paths to screenshots used in the manifest.json
        screenshots_with_rel_path = []

        rel_path_screenshots_dir = os.path.relpath(path=target_loc_screenshots_dir, start=path_output)

        for s in screenshot_references:

            old_ss_name = os.path.basename(s)
            new_ss_name = f"{uuid.uuid4().hex[:8]}_{old_ss_name}"

            rel_path_screenshot = f"{rel_path_screenshots_dir}/{new_ss_name}"
            new_screenshot_ref = f"{host_images_url}/{rel_path_screenshot}"

            screenshots_with_rel_path.append(rel_path_screenshot)

            shutil.copyfile(
                src=os.path.join(src_loc_screenshots_dir, old_ss_name),
                dst=os.path.join(target_loc_screenshots_dir, new_ss_name)
            )

            instructions_body = instructions_body.replace(s, new_screenshot_ref)

        return (instructions_body, screenshots_with_rel_path)

    def _handle_changelog(
        self,
        change_logs: dict,
    ) -> list:

        version_history: list[dict] = []

        if not change_logs:
            return version_history

        for change_log in change_logs:

            v = change_log.get("version")
            d = change_log.get("date")
            t = change_log.get("text")

            # We only add changes to the docs that have specified all required properties
            if not v or not d or not t:
                continue

            changes = t.split('\n')
            changes = [c.strip('+ ').strip() for c in changes if c]

            noetic_date = datetime.datetime.strptime(d, "%Y-%m-%d")

            # Because Rapid7 Extension Library uses this format by default, we have to convert it. See an example at:
            # https://github.com/rapid7/extension-library-content/blob/master/rapid7/extensions/workflow/Backup-Active-Workflows-to-Github/1.0.2/manifest.json
            r7_date = noetic_date.strftime('%m/%d/%Y')

            version_history.append({
                "version": v,
                "date": r7_date,
                "changes": " | ".join(changes)
            })

        return version_history

    def _generate_manifest_json(
            self,
            path_output: str,
            rel_path_logo: str,
            documentation_file_name: str,
            screenshots: list,
            manifest_data: dict
    ):
        HUB_MANIFEST_KEY_TAGS = "tags"

        path_manifest_json = os.path.join(path_output, "manifest.json")

        media = []

        for s in screenshots:
            media.append({
                "type": "image",
                "title": "",
                "source": s
            })

        file_output_data = {
            "id": manifest_data.get("id"),
            "title": manifest_data.get("name"),
            "version": manifest_data.get("version"),
            "overview": manifest_data.get("description"),
            "description": manifest_data.get("readme"),
            "logos": {
                "primary": rel_path_logo
            },
            "documentation": {
                "source": f"files/{documentation_file_name}",
                "type": "file"
            },
            "media": media,
            "publisher": "Rapid7",
            "rapid7Products": [
                {
                    "name": "SurfaceCommand",
                    "role": "primary"
                }
            ],
            "extension": {"type": "connector"}
        }

        # Handle categories
        file_output_data[HUB_MANIFEST_KEY_TAGS] = {}
        connector_categories = manifest_data.get("categories")

        if connector_categories and isinstance(connector_categories, list):

            file_output_data[HUB_MANIFEST_KEY_TAGS].update({
                "categories": connector_categories,
            })

        # Handle changelog
        version_history = self._handle_changelog(
            change_logs=manifest_data.get("changelog"),
        )

        if version_history:
            file_output_data.update({
                "versionHistory": version_history
            })

        sdk_helpers.print_log_msg(f"Writing manifest.json file to '{path_manifest_json}'")

        with open(path_manifest_json, "w") as fp:
            json.dump(file_output_data, fp, indent=2, sort_keys=True)

    def _generate_markdown(
        self,
        manifest_data: dict,
        path_connector: str
    ):

        hidden_types = []
        hidden_settings = []

        # Types are defined in files outside the manifest;
        # read properties of each type for inclusion in the generated doc.
        for typeref in manifest_data.get("types", []):
            typefile = os.path.join(path_connector, typeref.get("file", ""))
            if os.path.isfile(typefile):
                typedef = sdk_helpers.read_file(path_to_file=typefile)

                # Keep track of any hidden types
                if typedef.get("x-samos-hidden"):
                    hidden_types.append(typedef.get("x-samos-type-name"))
                    continue

                extends = typedef.get("x-samos-extends-types", [])
                typeref["title"] = typedef.get("title")
                typeref["extends"] = ", ".join([ext["type-name"] for ext in extends if ext not in hidden_types])

                typeref["correlates"] = {}
                for prop, propdef in typedef.get("properties", {}).items():
                    if "x-samos-correlation" in propdef:
                        supertype = propdef["x-samos-correlation"]["correlation-type"]
                        props = typeref["correlates"].get(supertype, [])
                        typeref["correlates"][supertype] = props + [propdef.get("title", prop)]
                for prop, propdef in typedef.get("x-samos-derived-properties", {}).items():
                    if "x-samos-correlation" in propdef:
                        supertype = propdef["x-samos-correlation"]["correlation-type"]
                        props = typeref["correlates"].get(supertype, [])
                        typeref["correlates"][supertype] = props + [propdef.get("title", prop)]

        # Filter out hidden types
        if hidden_types:
            manifest_data["types"] = [
                t for t in manifest_data.get("types")
                if t.get("id") not in hidden_types
            ]

        # If there are `settings` and one of them is a reference, we need to resolve it
        # NOTE: this is only to support settings with $refs. There is a more complete solution
        # for resolving documents in core: backend/python/noetic_common/libs/apps/refutils.py
        settings = manifest_data.get("settings")

        if settings:
            for i, setting in enumerate(settings):
                ref = setting.get("$ref")

                if ref:
                    settings[i] = sdk_helpers.resolve_ref(ref=ref, document=manifest_data)

                if setting.get("x-samos-hidden", False):
                    hidden_settings.append(setting.get("name"))

            # Filter out hidden settings
            if hidden_settings:
                manifest_data["settings"] = [
                    t for t in manifest_data.get("settings")
                    if t.get("name") not in hidden_settings
                ]

        # Separate import-feed from standard workflows
        noetic_workflows = []
        noetic_ingest_feeds = []
        all_noetic_workflows = manifest_data.get("workflows", [])
        for noetic_workflow in all_noetic_workflows:
            workflow_type = noetic_workflow.get("workflow_type")
            if workflow_type is None:
                noetic_workflows.append(noetic_workflow)
            elif workflow_type == "import":
                noetic_ingest_feeds.append(noetic_workflow)
            else:
                noetic_workflows.append(noetic_workflow)

        md = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_EXT_LIB_MD,
            templates_path=constants.TEMPLATE_PATH_DEV,
            autoescape=False,
            data={
                "app_manifest": manifest_data,
                "noetic_workflows": noetic_workflows,
                "noetic_ingest_feeds": noetic_ingest_feeds
            }
        )

        return md

    def _process_r7_docs(
        self,
        path_connector: str,
        path_base_output: str,
        host_images_url: str,
    ):

        path_manifest_file = os.path.join(path_connector, constants.MANIFEST_YAML)

        if not os.path.isfile(path_manifest_file):
            raise FileNotFoundError(f"No Manifest file found at {path_manifest_file}")

        # Get current connector data from manifest
        manifest_data = sdk_helpers.read_file(path_to_file=path_manifest_file)

        dir_name_connector = os.path.basename(path_connector)
        connector_version = manifest_data.get("version")
        connector_id = manifest_data.get("id", "").replace(".", "_")

        path_output = os.path.join(path_base_output, dir_name_connector, connector_version)
        host_images_url = f"{host_images_url}/{connector_id}/v{connector_version}"

        if not os.path.isdir(path_output):
            sdk_helpers.print_log_msg(
                f"Connector output directory not found. Creating '{path_output}'"
            )
            os.makedirs(path_output, exist_ok=True)

        # Create required doc directories
        path_dir_media = os.path.join(path_output, "media")
        os.makedirs(path_dir_media, exist_ok=True)

        path_dir_logo = os.path.join(path_dir_media, "logos")
        os.makedirs(path_dir_logo, exist_ok=True)

        path_dir_files = os.path.join(path_output, "files")
        os.makedirs(path_dir_files, exist_ok=True)

        rel_path_logo = self._copy_logo(
            path_output=path_output,
            src_loc_logo=os.path.join(path_connector, manifest_data.get("icon")),
            target_loc_logo=path_dir_logo
        )

        documentation_file_name = "instructions.md"

        # Get the instructions_body and any occurrences of screenshots that are mentioned
        instructions_body = manifest_data.get("requirements", "")
        screenshots = []

        regex = constants.REGEX_SS_REFERENCES
        screenshot_references = re.findall(regex, instructions_body)

        if screenshot_references:

            path_dir_screenshots = os.path.join(path_dir_media, "screenshots")
            os.makedirs(path_dir_screenshots, exist_ok=True)

            # NOTE: sometimes the path can be `/docs`` or `docs` or `.docs`
            # we handle those cases, horribly
            manipulated_path = os.path.dirname(screenshot_references[0]).replace(".", "")

            src_loc_screenshots_dir = f"{path_connector}{manipulated_path}"

            if not os.path.isdir(src_loc_screenshots_dir):
                src_loc_screenshots_dir = os.path.join(path_connector, manipulated_path)

                if not os.path.isdir(src_loc_screenshots_dir):
                    raise NotADirectoryError(f"'{src_loc_screenshots_dir}' is not a valid directory")

            instructions_body, screenshots = self._handle_screenshots(
                path_output=path_output,
                src_loc_screenshots_dir=src_loc_screenshots_dir,
                target_loc_screenshots_dir=path_dir_screenshots,
                instructions_body=instructions_body,
                screenshot_references=set(screenshot_references),
                host_images_url=host_images_url
            )

        self._generate_manifest_json(
            path_output=path_output,
            rel_path_logo=rel_path_logo,
            documentation_file_name=documentation_file_name,
            screenshots=screenshots,
            manifest_data=manifest_data
        )

        manifest_data["requirements"] = instructions_body

        # NOTE: do not support 'depends-on' yet in a surcom connector
        # when we do, we can reach out to the extension library with the connector_id to
        # get the connector name. Leaving this code pasted here for now.
        # connector_deps = sdk_helpers.get_connector_dependencies(
        #     depends_on=manifest_data.get("depends-on"),
        #     path_connector_repo=path_connector_repo
        # )

        # if connector_deps:
        #     manifest_data["connector_deps"] = connector_deps

        path_instructions = os.path.join(path_dir_files, documentation_file_name)

        sdk_helpers.print_log_msg(f"Generating Markdown and writing file to '{path_instructions}'")

        md = self._generate_markdown(manifest_data=manifest_data, path_connector=path_connector)

        # Write the __init__.py file
        sdk_helpers.write_file(
            path=path_instructions,
            contents=md.rendered_template
        )

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Generating docs for '{args.path_connector}'", divider=True)

        root_output_dir = os.path.join(args.dir_output, args.dir_structure)

        if not os.path.isdir(root_output_dir):
            LOG.debug("Root Directory '%s' not found. Creating it.", root_output_dir)
            os.makedirs(root_output_dir, exist_ok=True)

        host_images_url = f"{args.host_url}/{args.dir_structure}"

        self._process_r7_docs(
            path_connector=args.path_connector,
            path_base_output=root_output_dir,
            host_images_url=host_images_url
        )

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
