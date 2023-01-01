import requests
import os
import sys
import json
import argparse
from yaml import safe_load

def session_cookie(host, login, password):
    session = requests.Session()
    response = session.get(host)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"login": login, "password": password}
    session.post(response.url, headers=headers, data=data)
    session_cookie = session.cookies.get_dict()["authservice_session"]
    return session_cookie

def get_inference_server_status(
    deploy_environment:str, 
    model_name:str,
    hostname:str,
    ):

    # loading environments config
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'environments.yaml')
    with open(env_file_path, 'r') as yml:
        config = safe_load(yml)

    KUBEFLOW_ENDPOINT = config[deploy_environment]['kubeflow_endpoint']
    KUBEFLOW_USERNAME = config[deploy_environment]['kubeflow_username']
    KUBEFLOW_PASSWORD = config[deploy_environment]['kubeflow_password']

    # get session cookie of Kubeflow UI
    cookie = {"authservice_session": session_cookie(KUBEFLOW_ENDPOINT, KUBEFLOW_USERNAME, KUBEFLOW_PASSWORD)}

    # common vars
    MODEL_URL = f"{KUBEFLOW_ENDPOINT}/v1/models/{model_name}"
    HEADERS = {"Host": hostname}

    # testing model
    response = requests.get(MODEL_URL, headers=HEADERS, cookies=cookie)
    status_code = response.status_code

    # print("Status Code", status_code)
    # if status_code == 200:
    #     print("JSON Response ", json.dumps(response.json(), indent=2))

    return status_code


if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    parser.add_argument('-m', '--model-name', help="model name", required=True)
    parser.add_argument('-v', '--hostname', help="hostname", required=True)
    args = parser.parse_args()

    status_code = get_inference_server_status(
        deploy_environment=args.cloud_environment, 
        model_name=args.model_name,
        hostname=args.hostname
    )

    if status_code == 200:
        sys.exit(0)
    else:
        sys.exit(1)