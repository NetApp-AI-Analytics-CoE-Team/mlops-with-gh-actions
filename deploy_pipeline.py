from kfp import Client
from client import get_kubeflow_client
import argparse
import datetime
from yaml import safe_load

def deploy_pipeline(
    pipeline_yaml_path:str, 
    deploy_only:bool, 
    deploy_enviroment:str, 
    # experiment_name:str, 
    # namespace:str,
    pipeline_version_name:str=None, 
    ):

    # get kfp client connection
    client_info = get_kubeflow_client(deploy_enviroment)
    kfp_client = client_info["kfp_client"]   
    kfp_client.set_user_namespace(client_info["kfp_namespace"])
    experiment_name = client_info["kfp_experinment_name"]

    # check pipeline existence
    with open(pipeline_yaml_path, 'r') as yml:
        pipeline_yaml = safe_load(yml)
    pipeline_name = pipeline_yaml['spec']['entrypoint']
    pipeline_desc = pipeline_yaml['metadata']['annotations']
    pipeline_id = kfp_client.get_pipeline_id(pipeline_name)

    # upload package as a new pipeline if specified pipeline already exists
    if pipeline_id == None:
        pipeline_info = kfp_client.upload_pipeline(
            pipeline_package_path=pipeline_yaml_path,
            pipeline_name=pipeline_name,
            description=pipeline_desc
            )

        if deploy_only:
            print('new pipeline has been successfully uploaded')
            return pipeline_info

    # upload package as pipeline version if specified pipeline does not exist
    else:
        # if pipeline version name is not specified, use timestamp as pipeline version name
        if pipeline_version_name == None:
            t_delta = datetime.timedelta(hours=9)
            JST = datetime.timezone(t_delta, 'JST')
            now = datetime.datetime.now(JST)
            pipeline_version_name = now.strftime('%Y%m%d%H%M%S') # YYYYMMDDhhmmss

        pipeline_version_info = kfp_client.upload_pipeline_version(
            pipeline_package_path=pipeline_yaml_path,
            pipeline_name=pipeline_name,
            pipeline_version_name=pipeline_version_name,
            description=pipeline_desc
        )

        if deploy_only:
            print('pipeline version has been successfully uploaded')
            return pipeline_version_info

    # create run
    # run_pipeline()
    print('successfully launched the pipeline run')
    return("run_id")

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cloud-environment', help="specify 'on-prem' or 'cloud'", required=True)
    # parser.add_argument('-n', '--namespace', help="namespace where the pipeline runs", required=True)
    parser.add_argument('-f', '--pipeline-package-path', help="pipeline package path", required=True)
    parser.add_argument('-v', '--pipeline-version', help="pipeline version name")
    parser.add_argument('-d', '--deploy-only', action='store_true', help="specify if you don't want to run pipeline")
    # parser.add_argument('-e', '--experiment-name', help="existing experiment name(mandatory unless you specify -d/--deploy-only)")
    args = parser.parse_args()

    ret = deploy_pipeline(
        deploy_enviroment=args.cloud_environment, 
        pipeline_yaml_path=args.pipeline_package_path,
        pipeline_version_name=args.pipeline_version,
        deploy_only=args.deploy_only, 
        # namespace=args.namespace,
        # experiment_name=args.experiment_name, 
        )
    print(ret)