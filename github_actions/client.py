from kfp import Client
import argparse
from yaml import safe_load
import re
import requests
from urllib.parse import urlsplit
import os
import sys

def get_istio_auth_session(url: str, username: str, password: str) -> dict:
    """
    Determine if the specified URL is secured by Dex and try to obtain a session cookie.
    WARNING: only Dex `staticPasswords` and `LDAP` authentication are currently supported
             (we default default to using `staticPasswords` if both are enabled)

    :param url: Kubeflow server URL, including protocol
    :param username: Dex `staticPasswords` or `LDAP` username
    :param password: Dex `staticPasswords` or `LDAP` password
    :return: auth session information
    """
    # define the default return object
    auth_session = {
        "endpoint_url": url,    # KF endpoint URL
        "redirect_url": None,   # KF redirect URL, if applicable
        "dex_login_url": None,  # Dex login URL (for POST of credentials)
        "is_secured": None,     # True if KF endpoint is secured
        "session_cookie": None  # Resulting session cookies in the form "key1=value1; key2=value2"
    }

    # use a persistent session (for cookies)
    with requests.Session() as s:

        ################
        # Determine if Endpoint is Secured
        ################
        resp = s.get(url, allow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(
                f"HTTP status code '{resp.status_code}' for GET against: {url}"
            )

        auth_session["redirect_url"] = resp.url

        # if we were NOT redirected, then the endpoint is UNSECURED
        if len(resp.history) == 0:
            auth_session["is_secured"] = False
            return auth_session
        else:
            auth_session["is_secured"] = True

        ################
        # Get Dex Login URL
        ################
        redirect_url_obj = urlsplit(auth_session["redirect_url"])

        # if we are at `/auth?=xxxx` path, we need to select an auth type
        if re.search(r"/auth$", redirect_url_obj.path): 
            
            #######
            # TIP: choose the default auth type by including ONE of the following
            #######
            
            # OPTION 1: set "staticPasswords" as default auth type
            redirect_url_obj = redirect_url_obj._replace(
                path=re.sub(r"/auth$", "/auth/local", redirect_url_obj.path)
            )
            # OPTION 2: set "ldap" as default auth type 
            # redirect_url_obj = redirect_url_obj._replace(
            #     path=re.sub(r"/auth$", "/auth/ldap", redirect_url_obj.path)
            # )
            
        # if we are at `/auth/xxxx/login` path, then no further action is needed (we can use it for login POST)
        if re.search(r"/auth/.*/login$", redirect_url_obj.path):
            auth_session["dex_login_url"] = redirect_url_obj.geturl()

        # else, we need to be redirected to the actual login page
        else:
            # this GET should redirect us to the `/auth/xxxx/login` path
            resp = s.get(redirect_url_obj.geturl(), allow_redirects=True)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"HTTP status code '{resp.status_code}' for GET against: {redirect_url_obj.geturl()}"
                )

            # set the login url
            auth_session["dex_login_url"] = resp.url

        ################
        # Attempt Dex Login
        ################
        resp = s.post(
            auth_session["dex_login_url"],
            data={"login": username, "password": password},
            allow_redirects=True
        )
        if len(resp.history) == 0:
            raise RuntimeError(
                f"Login credentials were probably invalid - "
                f"No redirect after POST to: {auth_session['dex_login_url']}"
            )

        # store the session cookies in a "key1=value1; key2=value2" string
        auth_session["session_cookie"] = "; ".join([f"{c.name}={c.value}" for c in s.cookies])

    return auth_session

def get_kubeflow_client(environment:str):

    # loading environments config
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'environments.yaml')
    with open(env_file_path, 'r') as yml:
        config = safe_load(yml)

    KUBECONFIG_CONTEXT = config[environment]['kubeconfig_context']
    KUBEFLOW_ENDPOINT = config[environment]['kubeflow_endpoint']
    KUBEFLOW_USERNAME = config[environment]['kubeflow_username']
    KUBEFLOW_PASSWORD = config[environment]['kubeflow_password']
    KUBEFLOW_NAMESPACE = config[environment]['kubeflow_namespace']
    KUBEFLOW_EXPERIMENT_NAME = config[environment]['kubeflow_experiment_name']

    # get authentication for kubeflow
    auth_session = get_istio_auth_session(
        url=KUBEFLOW_ENDPOINT,
        username=KUBEFLOW_USERNAME,
        password=KUBEFLOW_PASSWORD
    )

    # connecting to the kubeflow pipeline API
    client = Client(
        host=f"{KUBEFLOW_ENDPOINT}/pipeline",
        kube_context=KUBECONFIG_CONTEXT,
        cookies=auth_session["session_cookie"])

    ret = {
        "kfp_client": client,
        "kfp_namespace": KUBEFLOW_NAMESPACE,
        "kfp_experinment_name": KUBEFLOW_EXPERIMENT_NAME,
        "kfp_endpoint": KUBEFLOW_ENDPOINT # for github actions
    }

    return ret

# for github actions
if __name__ == "__main__":
    ERR = "Usage: python3 FILE_NAME.py <ENVIRONMENT_NAME> <'namespace' or 'endpoint'>"

    if len(sys.argv) == 3:
        kfp_client_info = get_kubeflow_client(sys.argv[1])
        if sys.argv[2] == "namespace":
            print(kfp_client_info["kfp_namespace"])
        elif sys.argv[2] == "endpoint"
            print(kfp_client_info["kfp_endpoint"])
        else: 
            print(ERR)
            sys.exit(1)
    else:
        print(ERR)
        sys.exit(1)