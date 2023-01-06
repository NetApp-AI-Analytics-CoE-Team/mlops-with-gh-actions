from kserve import KServeClient
from kserve import constants
from kserve import V1beta1PredictorSpec
from kserve import V1beta1TFServingSpec
from kserve import V1beta1InferenceServiceSpec
from kserve import V1beta1InferenceService
from kubernetes import client
import requests
import os
import sys
import json
import argparse
from yaml import safe_load

def create_inference_server(
    namespace:str, 
    s3_region:str,
    s3_access_key_base64:str,
    s3_secret_key_base64:str,
    model_name:str,
    s3_uri:str
    ):

    # create temporary aws credential file
    aws_credintial_path = "/tmp/awscredentials"
    with open(aws_credintial_path, 'w') as awscred:
        awscred.write('[default]\n')
        awscred.write(f'aws_access_key_id = {s3_access_key_base64}\n')
        awscred.write(f'aws_secret_access_key = {s3_secret_key_base64}\n')

    # create client
    kserve = KServeClient()
    kserve.set_credentials(
        storage_type='S3',
        service_account=model_name, # create ServiceAccount as model name
        namespace=namespace,
        credentials_file=aws_credintial_path,
        s3_profile='default',
        s3_region=s3_region,
        s3_use_https='1',
    )

    # delete temporary credential file
    os.remove(aws_credintial_path)

    default_model_spec = V1beta1InferenceServiceSpec(
        predictor=V1beta1PredictorSpec(
            service_account_name='kserve-service-credentials',
            tensorflow=V1beta1TFServingSpec(storage_uri=s3_uri)
        ))

    isvc = V1beta1InferenceService(api_version=constants.KSERVE_V1BETA1,
                            kind=constants.KSERVE_KIND,
                            metadata=client.V1ObjectMeta(name=model_name, namespace=namespace),
                            spec=default_model_spec)

    # checking if there is a inference service which has same name as being about to created
    is_inference_serive_exist = kserve.get(model_name, namespace=namespace)

    # in case of inference serivce already exists
    if is_inference_serive_exist:
        try:
            kserve.replace(isvc, watch=True)
            return True
        except Exception as e:
            print(e)
            return False
    # in case of not existing, create a new inference service
    else:
        try:
            kserve.create(isvc, watch=True)
            return True
        except Exception as e:
            print(e)
            return False

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('--namespace', help="serving namespace", required=True)
    parser.add_argument('--region', help="region of the aritifact repository", required=True)
    parser.add_argument('--access-key-base64', help="base64 encoded access key of the aritifact repository", required=True)
    parser.add_argument('--secret-key-base64', help="base64 encoded secret key of the aritifact repository", required=True)
    parser.add_argument('--model-name', help="model name", required=True)
    parser.add_argument('--model-uri', help="s3 uri that stores model archive", required=True)
    args = parser.parse_args()

    ret = create_inference_server(
        namespace = args.namespace, 
        s3_region = args.region,
        s3_access_key_base64 = args.access_key_base64,
        s3_secret_key_base64 = args.secret_key_base64,
        model_name = args.model_name,
        s3_uri = args.model_uri
    )

    if ret:
        sys.exit(0)
    else:
        sys.exit(1)