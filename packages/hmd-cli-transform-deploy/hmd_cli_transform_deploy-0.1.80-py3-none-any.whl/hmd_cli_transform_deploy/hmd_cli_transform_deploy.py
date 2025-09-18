# Implement the lifecycle commands here
import datetime
import json
import os
import re
import subprocess
from time import sleep, time
from typing import Any, Dict, List
from hmd_cli_tools.hmd_cli_tools import (
    get_deployer_target_session,
    get_neuronsphere_domain,
    read_manifest,
)
from hmd_lib_transform.hmd_lib_transform import HmdLibTransform
from hmd_lib_auth.hmd_lib_auth import okta_service_account_token_by_service
from hmd_lib_librarian_client.artifact_tools import content_item_path_from_parts
from hmd_cli_tools.okta_tools import get_auth_token
from hmd_lib_naming.hmd_lib_naming import HmdNamingClient, Service
from InquirerPy import prompt
import shutil
import jwt
from pathlib import Path

# Grab hostname for locally running NeuronSphere
# This should only be set when running Robot Integration tests.
LOCALHOST = os.environ.get("HMD_NEURONSPHERE_LOCALHOST", "localhost")

LOCAL_URL = f"http://{LOCALHOST}/hmd_ms_transform/"


def get_transform_client(
    hmd_region: str,
    cust_code: str,
    environment: str,
):
    base_url = LOCAL_URL if environment == "local" else None
    auth_token = get_auth_token()

    if auth_token is None and environment == "local":
        auth_token = jwt.encode({"sub": "local-cli"}, "secret", algorithm="HS256")

    if base_url is None:
        naming_client = HmdNamingClient(
            base_url=f"https://ms-naming-aaa-{hmd_region}.{cust_code}-admin-neuronsphere.io",
            auth_token=auth_token,
        )
        transform_svc = naming_client.resolve_service(
            service=Service(name="ms-transform"), environment=environment
        )
        base_url = transform_svc.httpEndpoint

    transform_client = HmdLibTransform(base_url=base_url, auth_token=auth_token)

    return transform_client


def build(name: str, version: str):
    # Read the manifest.json file
    manifest = read_manifest()

    # Extract the value at "transforms.build.vars" path
    build_vars = manifest.get("transforms", {}).get("build", {}).get("vars", {})

    # Add "repo_name" and "repo_version" properties
    build_vars["repo_name"] = name
    build_vars["repo_version"] = version

    if os.path.exists("build/src/transforms"):
        shutil.rmtree("build/src/transforms")
    if os.path.exists("build/src/shared_schedules"):
        shutil.rmtree("build/src/shared_schedules")
    if os.path.exists("src/shared_schedules"):
        shutil.copytree("src/shared_schedules", "build/src/shared_schedules")

    # Process each file in src/transforms
    src_transforms_path = Path("src/transforms")
    build_transforms_path = Path("build/src/transforms")
    build_transforms_path.mkdir(parents=True, exist_ok=True)

    for file_path in src_transforms_path.rglob("*"):
        if file_path.suffix in [".yaml", ".yml", ".json"]:
            with open(file_path, "r") as file:
                content = file.read()
                for var, value in build_vars.items():
                    content = re.sub(rf"\${{{var}}}", value, content)
            build_file_path = build_transforms_path / file_path.relative_to(
                src_transforms_path
            )
            build_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(build_file_path, "w") as file:
                file.write(content)


def publish():
    pass


def deploy(
    name: str,
    version: str,
    profile: str,
    hmd_region: str,
    cust_code: str,
    environment: str,
    account: str,
    config: dict,
    force: bool = False,
):
    inst_name = config["dependencies"]["ms-transform"]["instance_name"]
    did = config["dependencies"]["ms-transform"]["deployment_id"]
    session = get_deployer_target_session(hmd_region, profile, account)
    token = okta_service_account_token_by_service(
        inst_name, "hmd-ms-transform", did, session
    )

    base_url = f"https://{inst_name}-{did}-{hmd_region}.{get_neuronsphere_domain(cust_code, environment)}"
    transform_client = HmdLibTransform(base_url=base_url, auth_token=token)

    artifact_path = content_item_path_from_parts(name, version, "build")
    force = config.get("force", force)
    resp = transform_client.deploy_transform_config(artifact_path, force)

    if isinstance(resp, str) and resp.startswith("Error"):
        raise Exception(resp)

    print(resp)


def load(project_name: str, transform_name: str):
    transform_client = HmdLibTransform(base_url=LOCAL_URL, api_key="local")

    result = transform_client.load_local_transform_configs(project_name, transform_name)
    for k in result:
        print(f"Loaded transform: {k}")


def get_transforms(
    hmd_region: str,
    cust_code: str,
    environment: str,
):
    transform_client = get_transform_client(hmd_region, cust_code, environment)

    result = transform_client.get_transforms()

    if result is None:
        print("Found no transforms")
        return

    print("Found Transforms:")
    for t in result:
        for name, value in t.items():
            print(f"{name} v{value['version']}: {value['status']}")


def check_transform_success(transform_client, inst, failed_instances):
    result = False
    # with Halo(text=f"Running: {inst}", spinner="dots") as spinner:
    print(f"Running: {inst['name']}")

    print(f"Transform Logs: \n")
    log_index = 0
    while not result:
        logs = transform_client.get_transform_inst_logs(instance_nid=inst["identifier"])
        logs_lines = logs.split("\n")
        print(
            "\n".join([f"[{inst['name']}]:  {line}" for line in logs_lines[log_index:]])
        )
        log_index = len(logs_lines) - 1
        attr = transform_client.search_transform_instances(name=inst["name"])
        if attr[0]["status"] == "complete_successful":
            # spinner.succeed(text=f"Completed: {inst}")
            print(f"Completed: {inst['name']}")
            return
        elif attr[0]["status"] == "complete_failed":
            # spinner.fail(text=f"Failed: {inst}")
            print(f"Failed: {inst['name']}")
            failed_instances.append(attr[0]["identifier"])
            return
        elif attr[0]["status"] == "scheduling_failed":
            # spinner.fail(text=f"Scheduling failed: {inst}")
            print(f"Scheduling failed: {inst['name']}")
            failed_instances.append(attr[0]["identifier"])
            return
        else:
            sleep(10)
            attr = transform_client.search_transform_instances(name=inst["name"])


def check_transform_status(transform_client, scheduled):
    failed_instances = []
    for inst in scheduled:
        check_transform_success(transform_client, inst, failed_instances)

    if len(failed_instances) > 0:
        raise Exception(f"failed instances: {failed_instances}")
    else:
        print("All transforms completed successfully.")


def _get_transform_names(transform_client, transform_names=None):
    questions = []

    if transform_names is None:
        transforms = transform_client.get_transforms()

        questions.append(
            {
                "type": "checkbox",
                "name": "transform_names",
                "message": "Select transforms",
                "choices": sorted(
                    [
                        {"name": f"{name}@{value['version']}", "value": name}
                        for t in transforms
                        for name, value in t.items()
                    ],
                    key=lambda tf: tf["name"],
                ),
            }
        )

    result = {}
    if len(questions) > 0:
        result = prompt(questions)
        selected_transforms = result.get("transform_names", [])
        if transform_names is None:
            transform_names = [t.split("@")[0] for t in selected_transforms]

    return transform_names


def run_transforms(
    hmd_region: str,
    cust_code: str,
    environment: str,
    transform_names: List[str] = None,
    run_params: Dict[str, Any] = None,
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )
    transform_names = _get_transform_names(
        transform_client=transform_client, transform_names=transform_names
    )

    if transform_names is None or len(transform_names) == 0:
        print("Must select at least one transform to run")
        return

    selected_transforms = transform_names

    transform_run = {t.split("@")[0]: {} for t in selected_transforms}

    for tf in transform_run.keys():
        tf_config = transform_client.base_client.invoke_custom_operation(
            "get_transform_config", {"transform": {"name": tf}}, "POST"
        )
        if run_params is None:
            questions = []
            if "image_sequence" in tf_config:
                for index, img in enumerate(tf_config["image_sequence"]):
                    questions.append(
                        {
                            "type": "input",
                            "name": f"container_env_{index}",
                            "message": f"Container {index} Env:",
                            "default": json.dumps(img.get("env", {}), indent=2),
                            "multiline": True,
                        }
                    )
            else:
                questions.append(
                    {
                        "type": "input",
                        "name": "run_params",
                        "message": "Run Paramaters:",
                        "default": json.dumps(
                            tf_config.get("run_params", {}), indent=2
                        ),
                        "multiline": True,
                    }
                )

            result = prompt(questions)
            if "image_sequence" in tf_config:
                for index, img in enumerate(tf_config["image_sequence"]):
                    if result.get(f"container_env_{index}") is None:
                        return
                    env = json.loads(result.get(f"container_env_{index}"))
                    tf_config["image_sequence"][index]["env"] = env

                transform_run[tf] = tf_config["image_sequence"]
            else:
                if result.get("run_params") is None:
                    return
                run_params = json.loads(result.get("run_params"))
                transform_run[tf] = run_params
                run_params = None
        else:
            if "image_sequence" in tf_config:
                envs = run_params
                for index, env in enumerate(envs):
                    tf_config["image_sequence"][index]["env"] = env
                transform_run[tf] = tf_config["image_sequence"]
                continue
            transform_run[tf] = run_params

    if transform_names is None:
        transform_names = transform_run.keys()

    retry = []
    scheduled = []
    retried = []
    for name in transform_names:
        print(f"Running: {name}, {json.dumps(transform_run[name])}")
        inst = transform_client.run_provider_transform(name, transform_run[name])
        if inst["status"] == "scheduling_failed":
            print(f"{name} failed to schedule.")
            retry.append(name)
        else:
            scheduled.append(
                {"name": inst["instance_name"], "identifier": inst["identifier"]}
            )
    print("Transforms scheduled. Checking for failures..")
    if len(retry) > 0:
        print(f"Retrying {len(retry)} failed instances..")
        for name in retry:
            inst = transform_client.run_provider_transform(name, transform_run[name])
            if inst["status"] == "scheduling_failed":
                retried.append(name)
            else:
                scheduled.append({inst["instance_name"]: inst["identifier"]})
    if len(retried) > 0:
        raise Exception(f"Unable to schedule the following transforms: {retried}")

    for s in scheduled:
        for k, v in s.items():
            print(f"{k} scheduled with identifier: {v}")

    check_transform_status(transform_client, scheduled)
    return scheduled


def submit_transform(
    hmd_region: str,
    cust_code: str,
    environment: str,
    transform_names: List[str] = None,
    nids: List[str] = None,
):
    if environment == "local":
        print("Cannot submit transforms in local environment")
        return

    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )
    transform_names = _get_transform_names(
        transform_client=transform_client, transform_names=transform_names
    )

    if transform_names is None or len(transform_names) == 0:
        print("Must select at least one transform to run")
        return

    transform_names = [t.split("@")[0] for t in transform_names]
    instances = []
    for name in transform_names:
        try:
            insts = transform_client.submit_transform(name, nids)
            instances.extend(insts)
            print(f"Scheduled: {insts}")
        except:
            print(f"Failed scheduling {name}")

    check_transform_status(transform_client, instances)
    return instances


def get_instance_logs(
    hmd_region: str, cust_code: str, environment: str, instance_nid: str
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    transform_client.get_transform_inst_logs(instance_nid=instance_nid)


def get_backfill_results(
    hmd_region: str, cust_code: str, environment: str, backfill_id: str
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    return transform_client.get_backfill_results(backfill_id)


def monitor_backfill(
    hmd_region: str,
    cust_code: str,
    environment: str,
    backfill_id: str,
    dry_run: bool = True,
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    status_resp = transform_client.get_backfill_status(backfill_id)

    while status_resp.get("status") in ["pending", "querying"]:
        sleep(5)
        status_resp = transform_client.get_backfill_status(backfill_id)

    if status_resp.get("status") == "failed":
        raise Exception("Backfill event failed")

    if status_resp.get("status") in ["no_entities", "entities_identified"]:
        backfill_results = transform_client.get_backfill_results(backfill_id)
        print(f"Backfill event results: {json.dumps(backfill_results, indent=2)}")

    if not dry_run:
        while status_resp.get("status") not in ["failed", "completed"]:
            sleep(5)
            status_resp = transform_client.get_backfill_status(backfill_id)
            print(f"Backfill event status: {json.dumps(status_resp, indent=2)}")

        if status_resp.get("status") == "failed":
            raise Exception("Backfill event failed")

        if status_resp.get("status") == "completed":
            backfill_results = transform_client.get_backfill_results(backfill_id)
            print(f"Backfill event results: {json.dumps(backfill_results, indent=2)}")


def backfill_transform(
    hmd_region: str,
    cust_code: str,
    environment: str,
    transform_name: str,
    filter_string: str,
    dry_run: bool = True,
    priority: int = 5,
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    result = transform_client.backfill_transform_query(
        transform_name, filter_string, dry_run=dry_run, priority=priority
    )

    return result


def backfill_instances(
    hmd_region: str,
    cust_code: str,
    environment: str,
    transform_name: str,
    status: str,
    start_time: str,
    end_time: str,
    dry_run: bool = True,
    priority: int = 5,
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    result = transform_client.backfill_instances(
        transform_name,
        status,
        (
            start_time
            if start_time is None
            else datetime.datetime.fromisoformat(start_time)
        ),
        end_time if end_time is None else datetime.datetime.fromisoformat(end_time),
        dry_run=dry_run,
        priority=priority,
    )

    return result


def run_backfill(
    hmd_region: str,
    cust_code: str,
    environment: str,
    backfill_id: str,
    priority: int = 5,
):

    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    result = transform_client.run_backfill(backfill_id, priority=priority)

    return result


def list_backfill_events(
    hmd_region: str,
    cust_code: str,
    environment: str,
    since_date: str = (
        datetime.datetime.now() - datetime.timedelta(days=7)
    ).isoformat(),
):
    transform_client = get_transform_client(
        hmd_region=hmd_region, cust_code=cust_code, environment=environment
    )

    return transform_client.list_backfill_events(since_date=since_date)
