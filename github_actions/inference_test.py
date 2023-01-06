import requests
import os
import sys
import json
import argparse
from yaml import safe_load
import PIL.Image
import numpy as np

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
    kubeflow_endpoint:str,
    kubeflow_username:str,
    kubeflow_password:str,
    model_name:str,
    hostname:str,
    ):

    # get session cookie of Kubeflow UI
    cookie = {"authservice_session": session_cookie(kubeflow_endpoint, kubeflow_username, kubeflow_password)}

    # common vars
    MODEL_URL = f"{kubeflow_endpoint}/v1/models/{model_name}"
    HEADERS = {"Host": hostname}

    # testing model
    response = requests.get(MODEL_URL, headers=HEADERS, cookies=cookie)
    status_code = response.status_code

    # print("Status Code", status_code)
    if status_code != 200:
        print("JSON Response ", json.dumps(response.json(), indent=2))

    return status_code

def post_inference_request(
    kubeflow_endpoint:str,
    kubeflow_username:str,
    kubeflow_password:str,
    model_name:str,
    hostname:str,
    ):

    # download some flower images
    url='https://cdn.pixabay.com/photo/2016/08/28/23/24/sunflower-1627193_1280.jpg'
    image_path='/tmp/sunflower.jpg'
    urlData = requests.get(url).content
    with open(image_path ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)

    image = PIL.Image.open(image_path).convert("RGB").resize((299, 299))
    image = np.array(image) / 255
    image_list = image.tolist()
    payload = {
        "instances": [image_list]
    }

    # get session cookie of Kubeflow UI
    cookie = {"authservice_session": session_cookie(kubeflow_endpoint, kubeflow_username, kubeflow_password)}

    # common vars
    MODEL_URL = f"{kubeflow_endpoint}/v1/models/{model_name}:predict"
    HEADERS = {"Host": hostname}

    # testing model
    response = requests.post(MODEL_URL, headers=HEADERS, cookies=cookie, json=payload)
    status_code = response.status_code

    # print("Status Code", status_code)
    if status_code != 200:
        print("JSON Response ", json.dumps(response.json(), indent=2))

    return status_code

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', help="kubeflow endpoint", required=True)
    parser.add_argument('--username', help="kubeflow username", required=True)
    parser.add_argument('--password', help="kubeflow password", required=True)
    parser.add_argument('--model-name', help="model name", required=True)
    parser.add_argument('--hostname', help="hostname", required=True)
    args = parser.parse_args()

    # get server status
    status_code_get = get_inference_server_status(
        kubeflow_endpoint=args.endpoint, 
        kubeflow_username=args.username, 
        kubeflow_password=args.password, 
        model_name=args.model_name,
        hostname=args.hostname
    )
    # verify server is running
    if status_code_get == 200:
        print("INFO: Inference server is running")
    else:
        print("ERROR: Inference server is NOT healthy")
        sys.exit(1)

    # request inference
    status_code_post = post_inference_request(
        kubeflow_endpoint=args.endpoint, 
        kubeflow_username=args.username, 
        kubeflow_password=args.password,  
        model_name=args.model_name,
        hostname=args.hostname
    )

    # verify 
    if status_code_post == 200:
        print("INFO: Inference request is successfully processed")
        sys.exit(0)
    else:
        print("ERROR: Inference request failed")
        sys.exit(1)