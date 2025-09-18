import json
from cement import Controller, ex
from importlib.metadata import version
from hmd_cli_tools.hmd_cli_tools import get_standard_parameters, load_hmd_env

VERSION_BANNER = """
hmd  version: {}
"""

VERSION = version("hmd_cli_transform_deploy")


class LocalController(Controller):
    class Meta:
        label = "transform"

        stacked_type = "nested"
        stacked_on = "base"

        # text displayed at the top of --help output
        description = "Command for deploying transforms"

        arguments = (
            (
                ["-v", "--version"],
                {
                    "help": "Display the version of the  command.",
                    "action": "version",
                    "version": VERSION_BANNER.format(VERSION),
                },
            ),
        )

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

    @ex(help="build transform projects")
    def build(self):
        from .hmd_cli_transform_deploy import build as do_build

        name = self.app.pargs.repo_name
        version = self.app.pargs.repo_version

        result = do_build(name, version)

    @ex(help="publish a transform project")
    def publish(self):
        from .hmd_cli_transform_deploy import publish as do_publish

        result = do_publish()

    @ex(
        help="deploy transforms and shared schedules",
        arguments=get_standard_parameters()
        + [
            (
                ["-f", "--force"],
                {
                    "help": "Forces re-deployment of transform configs.",
                    "action": "store_true",
                    "dest": "force",
                    "default": False,
                },
            ),
        ],
    )
    def deploy(self):
        name = self.app.pargs.repo_name
        version = self.app.pargs.repo_version
        profile = self.app.pargs.profile
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        account = self.app.pargs.account
        config = self.app.pargs.config_values
        try:
            args = {
                "name": name,
                "version": version,
                "profile": profile,
                "hmd_region": hmd_region,
                "cust_code": cust_code,
                "environment": environment,
                "account": account,
                "config": config,
            }

            if hasattr(self.app.pargs, "force"):
                force = self.app.pargs.force
                args.update({"force": force})

            from .hmd_cli_transform_deploy import deploy as do_deploy

            result = do_deploy(**args)
            print(result)
        except Exception as e:
            print(f"Error deploying transform: {e}")

    @ex(help="list all deployed transforms", arguments=get_standard_parameters())
    def get_transforms(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment

        from .hmd_cli_transform_deploy import get_transforms as do_get_transforms

        result = do_get_transforms(
            hmd_region=hmd_region, cust_code=cust_code, environment=environment
        )

    @ex(
        help="load transforms from project to local transform service",
        arguments=[
            (
                ["-prj", "--project"],
                {
                    "help": "name of project containing transforms",
                    "action": "store",
                    "dest": "project",
                },
            ),
            (
                ["-tn", "--transform-name"],
                {
                    "help": "name of transform",
                    "action": "store",
                    "dest": "transform_name",
                },
            ),
        ],
    )
    def load_local(self):
        load_hmd_env(override=False)
        project_name = self.app.pargs.project
        transform_name = self.app.pargs.transform_name

        from .hmd_cli_transform_deploy import load as do_load

        result = do_load(project_name, transform_name)

    @ex(
        help="run one or more transforms",
        arguments=[
            *get_standard_parameters(),
            (
                ["-tf", "--transform"],
                {
                    "help": "name of transform",
                    "nargs": "*",
                    "action": "store",
                    "dest": "transform_names",
                },
            ),
            (
                ["-rp", "--run-params"],
                {
                    "help": "JSON string of run parameters",
                    "action": "store",
                    "dest": "run_params",
                },
            ),
        ],
    )
    def run_transforms(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        transform_names = self.app.pargs.transform_names
        config_file = self.app.pargs.config_file
        run_params = self.app.pargs.run_params

        if run_params is not None:
            run_params = json.loads(run_params)
        elif config_file is not None:
            with open(config_file, "r") as cf:
                run_params = json.load(cf)

        from .hmd_cli_transform_deploy import run_transforms as do_run_transforms

        result = do_run_transforms(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            transform_names=transform_names,
            run_params=run_params,
        )

    @ex(
        help="submit one or more transforms",
        arguments=[
            *get_standard_parameters(["environment"]),
            (
                ["-tf", "--transform"],
                {
                    "help": "name of transform",
                    "nargs": "*",
                    "action": "store",
                    "dest": "transform_names",
                },
            ),
            (
                ["-nid", "--idnetifiers"],
                {
                    "help": "list of entity nids to run against",
                    "action": "store",
                    "nargs": "*",
                    "dest": "nids",
                },
            ),
        ],
    )
    def submit_transforms(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        transform_names = self.app.pargs.transform_names
        nids = self.app.pargs.nids

        from .hmd_cli_transform_deploy import submit_transform as do_submit_transform

        result = do_submit_transform(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            transform_names=transform_names,
            nids=nids,
        )

    @ex(
        help="get logs for a transform",
        arguments=[
            *get_standard_parameters(),
            (
                ["-ti", "--transform-instance-nid"],
                {
                    "help": "NID of transform instance",
                    "action": "store",
                    "dest": "instance_nid",
                    "required": True,
                },
            ),
        ],
    )
    def get_logs(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        instance_nid = self.app.pargs.instance_nid

        from .hmd_cli_transform_deploy import get_instance_logs as do_get_logs

        do_get_logs(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            instance_nid=instance_nid,
        )

    @ex(
        help="backfill a transform based on graph query",
        arguments=[
            *get_standard_parameters(["environment"]),
            (
                ["-tf", "--transform"],
                {
                    "help": "name of transform",
                    "action": "store",
                    "dest": "transform_name",
                    "required": True,
                },
            ),
            (
                ["-f", "--filter"],
                {
                    "help": "graph query filter string",
                    "action": "store",
                    "dest": "filter_string",
                    "required": True,
                },
            ),
            (
                ["--no-dry-run"],
                {
                    "help": "disable dry run",
                    "action": "store_true",
                    "dest": "no_dry_run",
                },
            ),
            (
                ["-p", "--priority"],
                {
                    "help": "set the priority of the backfill",
                    "action": "store",
                    "dest": "priority",
                    "default": 5,
                },
            ),
        ],
    )
    def backfill_transform(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        transform_names = self.app.pargs.transform_name
        filter_string = self.app.pargs.filter_string
        no_dry_run = self.app.pargs.no_dry_run
        priority = self.app.pargs.priority

        from .hmd_cli_transform_deploy import (
            backfill_transform as do_backfill_transform,
            monitor_backfill,
        )

        result = do_backfill_transform(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            transform_name=transform_names,
            filter_string=filter_string,
            dry_run=not no_dry_run,
            priority=priority,
        )

        print(f"Backfill event: {json.dumps(result, indent=2)}")

        backfill_id = result.get("identifier")

        if backfill_id is None:
            raise Exception("Failed to create backfill event")

        monitor_backfill(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            backfill_id=backfill_id,
            dry_run=not no_dry_run,
        )

    @ex(
        help="backfill transform instances",
        arguments=[
            *get_standard_parameters(["environment"]),
            (
                ["-tf", "--transform"],
                {
                    "help": "name of transform",
                    "action": "store",
                    "dest": "transform_name",
                    "required": True,
                },
            ),
            (
                ["-s", "--status"],
                {
                    "help": "instance status filter",
                    "action": "store",
                    "dest": "status_filter",
                    "required": True,
                },
            ),
            (
                ["-st", "--start-time"],
                {
                    "help": "start time filter",
                    "action": "store",
                    "dest": "start_time",
                },
            ),
            (
                ["-et", "--end-time"],
                {
                    "help": "end time filter",
                    "action": "store",
                    "dest": "end_time",
                },
            ),
            (
                ["--no-dry-run"],
                {
                    "help": "disable dry run",
                    "action": "store_true",
                    "dest": "no_dry_run",
                },
            ),
            (
                ["-p", "--priority"],
                {
                    "help": "set the priority of the backfill",
                    "action": "store",
                    "dest": "priority",
                    "default": 5,
                },
            ),
        ],
    )
    def backfill_instances(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        transform_name = self.app.pargs.transform_name
        status_filter = self.app.pargs.status_filter
        start_time = self.app.pargs.start_time
        end_time = self.app.pargs.end_time
        no_dry_run = self.app.pargs.no_dry_run
        priority = self.app.pargs.priority

        from .hmd_cli_transform_deploy import (
            backfill_instances as do_backfill_instances,
            monitor_backfill,
        )

        result = do_backfill_instances(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            transform_name=transform_name,
            status=status_filter,
            start_time=start_time,
            end_time=end_time,
            dry_run=not no_dry_run,
            priority=priority,
        )

        print(f"Backfill event: {json.dumps(result, indent=2)}")

        backfill_id = result.get("identifier")

        if backfill_id is None:
            raise Exception("Failed to create backfill event")

        monitor_backfill(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            backfill_id=backfill_id,
            dry_run=not no_dry_run,
        )

    @ex(
        help="list backfill events",
        arguments=[
            *get_standard_parameters(["environment"]),
            (
                ["-s", "--since"],
                {
                    "help": "list backfill events since this time",
                    "action": "store",
                    "dest": "since_date",
                },
            ),
        ],
    )
    def list_backfill_events(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        since_date = self.app.pargs.since_date

        from .hmd_cli_transform_deploy import (
            list_backfill_events as do_list_backfill_events,
        )

        events = do_list_backfill_events(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            since_date=since_date,
        )
        for event in events:
            print(json.dumps(event, indent=2))

    @ex(
        help="run backfill event",
        arguments=[
            *get_standard_parameters(["environment"]),
            (
                ["-b", "--backfill-id"],
                {
                    "help": "ID of the backfill event to run",
                    "action": "store",
                    "dest": "backfill_id",
                    "required": True,
                },
            ),
        ],
    )
    def run_backfill(self):
        load_hmd_env(override=False)
        hmd_region = self.app.pargs.hmd_region
        cust_code = self.app.pargs.customer_code
        environment = self.app.pargs.environment
        backfill_id = self.app.pargs.backfill_id

        from .hmd_cli_transform_deploy import (
            run_backfill as do_run_backfill,
            monitor_backfill,
        )

        result = do_run_backfill(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            backfill_id=backfill_id,
        )

        print(f"Run backfill event: {json.dumps(result, indent=2)}")

        monitor_backfill(
            hmd_region=hmd_region,
            cust_code=cust_code,
            environment=environment,
            backfill_id=backfill_id,
            dry_run=False,
        )
