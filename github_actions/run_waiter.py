from kfp import Client
from client import get_kubeflow_client
import argparse
import time
import sys

def run_waiter(
    deploy_environment:str,
    run_id: str,
    check_interval_sec:int=60,
    retry_count:int=60):

    # get kfp client connection
    client_info = get_kubeflow_client(deploy_environment)
    kfp_client = client_info["kfp_client"]   
    kfp_client.set_user_namespace(client_info["kfp_namespace"])

    while retry_count >= 0:
        run_info = kfp_client.get_run(run_id=run_id)
        # print(run_info.run.name)
        # print(run_info.run.status)
        # print(run_info.run.finished_at)

        # status should be "Succeeded" or "Failed" or "Running"
        if run_info.run.status != "Running":
            run_status = run_info.run.status
            break
        
        # if the Run does not end in specified retry count, return with "Unknown" status 
        if retry_count == 0:
            print("Running out of retry counts. To check status of the RUN, access the Kubeflow UI directly.")
            run_status = "Unknown"
            break
    
        print("Pipeline is still running. Waiting for check interval... (Remaining retry count: " + str(retry_count) + ")")
        time.sleep(check_interval_sec)
        retry_count = retry_count - 1
    
    return run_status


if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    parser.add_argument('-r', '--run-id', help="Run ID you want to check status", required=True)
    args = parser.parse_args()

    run_result = run_waiter(
        deploy_environment=args.cloud_environment,
        run_id=args.run_id
    )

    print(f"Status: {run_result}") 
    if run_result == "Succeeded":
        sys.exit(0)
    else:
        sys.exit(1)
