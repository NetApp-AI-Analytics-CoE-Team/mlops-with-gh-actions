# get artifact from existing RUN
#
# This code is from this issue
# https://github.com/kubeflow/pipelines/issues/4327

import json
import tarfile
import argparse
import sys
from base64 import b64decode
from io import BytesIO
from client import get_kubeflow_client
import kfp


def get_node_id(*, run_id: str, component_name: str, client: kfp.Client):
    run = client.runs.get_run(run_id)
    workflow = json.loads(run.pipeline_runtime.workflow_manifest)
    nodes = workflow["status"]["nodes"]
    for node_id, node_info in nodes.items():
        if node_info["displayName"] == component_name:
            return node_id
    else:
        raise RuntimeError(f"Unable to find node_id for Component '{component_name}'")


def get_artifact(*, run_id: str, node_id: str, artifact_name: str, client: kfp.Client):
    artifact = client.runs.read_artifact(run_id, node_id, artifact_name)
    # Artifacts are returned as base64-encoded .tar.gz strings
    data = b64decode(artifact.data)
    io_buffer = BytesIO()
    io_buffer.write(data)
    io_buffer.seek(0)
    data = None
    with tarfile.open(fileobj=io_buffer) as tar:
        member_names = tar.getnames()
        if len(member_names) == 1:
            data = tar.extractfile(member_names[0]).read().decode('utf-8')
        else:
            # Is it possible for KFP artifacts to have multiple members?
            data = {}
            for member_name in member_names:
                data[member_name] = tar.extractfile(member_name).read().decode('utf-8')
    return data


if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    parser.add_argument('-r', '--run-id', help="Run ID you want to check status", required=True)
    parser.add_argument('-n', '--component-name', help="component name", required=True)
    parser.add_argument('-a', '--artifact-name', help="artifact name", required=True)
    args = parser.parse_args()

    # get kfp client connection
    client_info = get_kubeflow_client(args.cloud_environment)
    kfp_client = client_info["kfp_client"]   
    kfp_client.set_user_namespace(client_info["kfp_namespace"])

    node_id = get_node_id(run_id=args.run_id, component_name=args.component_name, client=kfp_client)
    artifact = get_artifact(
        run_id=args.run_id, node_id=node_id, artifact_name=args.artifact_name, client=kfp_client,
    )
    sys.stdout.write(artifact)