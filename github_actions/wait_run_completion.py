from kfp import Client
from client import get_kubeflow_client
import argparse
import time
import sys

# wait for pipeline RUN's completion
def run_waiter(
    kfp_client_dict:dict,
    kfp_namespace:str,
    run_id: str,
    timeout_seconds:int=18000 # 5 hours
    ):

    # get kfp client connection
    kfp_client = kfp_client_dict["data"]   
    kfp_client.set_user_namespace(kfp_namespace)

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
    parser.add_argument('--k8s-context', help="kubeconfig context name", required=True)
    parser.add_argument('--kf-endpoint', help="kubeflow endpoint", required=True)
    parser.add_argument('--kf-username', help="kubeflow username", required=True)
    parser.add_argument('--kf-password', help="kubeflow password", required=True)
    parser.add_argument('--namespace', help="kubeflow profile", required=True)
    parser.add_argument('--run-id', help="Run ID you want to check status", required=True)
    parser.add_argument('--output-file', help="specify file path if you want to store output into a file")
    # parser.add_argument('-t', '--timeout-seconds', help="timeout seconds", required=True)
    args = parser.parse_args()

    # get kfp client
    kfp_client_dict = get_kubeflow_client(
        kubeconfig_context = args.k8s_context,
        kubeflow_endpoint = args.kf_endpoint,
        kubeflow_username = args.kf_username,
        kubeflow_password = args.kf_password
    )

    run_result = run_waiter(
        kfp_client_dict = kfp_client_dict, 
        kfp_namespace = args.namespace,
        run_id=args.run_id,
        # timeout_seconds=args.timeout_seconds
    )
    
    # for github actions
    if args.output_file:
        with open(args.output_file, mode='w') as f:
            f.write(run_result)

    sys.exit(0)
