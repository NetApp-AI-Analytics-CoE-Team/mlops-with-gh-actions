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
    deploy_environment:str, 
    model_name:str,
    s3_uri:str
    ):
    # loading environments config
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'environments.yaml')
    with open(env_file_path, 'r') as yml:
        config = safe_load(yml)
    NAMESPACE = config[deploy_environment]['serving_namespace']
    S3_REGION = config[deploy_environment]['artifact_repository']['s3_region']
    S3_ACCESS_KEY = config[deploy_environment]['artifact_repository']['s3_access_key_base64']
    S3_SECRET_KEY = config[deploy_environment]['artifact_repository']['s3_secret_key_base64']

    # create temporary aws credential file
    aws_credintial_path = "/tmp/awscredentials"
    with open(aws_credintial_path, 'w') as awscred:
        awscred.write('[default]\n')
        awscred.write(f'aws_access_key_id = {S3_ACCESS_KEY}\n')
        awscred.write(f'aws_secret_access_key = {S3_SECRET_KEY}\n')

    # create client
    kserve = KServeClient()
    kserve.set_credentials(
        storage_type='S3',
        service_account=model_name # create ServiceAccount as model name
        namespace=NAMESPACE,
        credentials_file=aws_credintial_path,
        s3_profile='default',
        s3_region=S3_REGION,
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
                            metadata=client.V1ObjectMeta(name=model_name, namespace=NAMESPACE),
                            spec=default_model_spec)

    # create inference server
    try:
        kserve.create(isvc, watch=True)
        return True
    except:
        return False

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    parser.add_argument('-m', '--model-name', help="model name", required=True)
    parser.add_argument('-u', '--model-uri', help="s3 uri that stores model archive", required=True)
    args = parser.parse_args()

    ret = create_inference_server(
        deploy_environment=args.cloud_environment, 
        model_name=args.model_name,
        s3_uri=args.model_uri
    )

    if ret:
        sys.exit(0)
    else:
        sys.exit(1)