from kfp import Client
from client import get_kubeflow_client
import argparse
import time
import sys

# wait for pipeline RUN's completion
def run_waiter(
    deploy_environment:str,
    run_id: str,
    timeout_seconds:int=18000 # 5 hours
    ):

    # get kfp client connection
    client_info = get_kubeflow_client(deploy_environment)
    kfp_client = client_info["kfp_client"]   
    kfp_client.set_user_namespace(client_info["kfp_namespace"])

    try:
        run_info = kfp_client.wait_for_run_completion(run_id=run_id, timeout=timeout_seconds)
        print(run_info)
        return run_info.run.status
    except TimeoutError as e:
        print(e)
        return ("TimeoutError")

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    parser.add_argument('-r', '--run-id', help="Run ID you want to check status", required=True)
    parser.add_argument('-o', '--output-file', help="specify file path if you want to store output into a file")
    # parser.add_argument('-t', '--timeout-seconds', help="timeout seconds", required=True)
    args = parser.parse_args()

    run_result = run_waiter(
        deploy_environment=args.cloud_environment,
        run_id=args.run_id,
        # timeout_seconds=args.timeout_seconds
    )
    
    # for github actions
    if args.output_file:
        with open(args.output_file, mode='w') as f:
            f.write(run_result)

    sys.exit(0)
