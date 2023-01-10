# About this repository
This repo is intended to use for demonstration of some **MLOps** tasks

## About Github Actions
This repo has Github Actions that provide two type of workflows.

    1. Workflow for model training
        - it is initiated when PR opened and you issue a PR command 
    2. Workflows for model serving
        - it is initiated when PR merged to "develeopent" or "main" branch

# Prerequisite
- K8s Clusters
    - Training cluster
        - Kubeflow (installed as multi user mode)
        - You can use same cluster as both for Training and for Serving 
    - Serving cluster
        - Kubeflow (installed as multi user mode)
        - You can use same cluster as both for Training and for Serving 
- GitHub App installed
- Self-hosted GitHub Actions Runner
    - kubeconfig(~/.kube/config) that associated with Training and Serving cluster
    - aws s3 credentials(~/.aws/credentials) to your artifact repository
    - python libraries stated in "requirements.txt"


# How to use
## Initial Setup
### On your GitHub repository
1. Create enviroments named as below in you GitHub repository
- Training: envroment that Kubeflow Pipelines runs on 
- Staging: 
- Production

2. Create a branch named "development"

3. Define secrets under each environments as below
- Under **Training** environment
    - K8S_CONTEXT
        - context name that is defined in kubeconfig in your github actions runner
    - KUBEFLOW_ENDPOINT
        - Kubeflow endpoint's URL (i.e. https://kubeflow.exmaple.com) 
    - KUBEFLOW_USERNAME
        - Your Kubeflow username which have right permission to access **training** tenant
    - KUBEFLOW_PASSWORD
        - Your Kubeflow password which have right permission to access **training** tenant
    - KUBEFLOW_EXPERIMENT_NAME
        - Existing experiment name on your Kubeflow profile
    - NAMESPACE
        - Kubeflow profile name(=k8s namespace) where your ML training pipelines run on

- Under **Staging** environment
    - ARTIFACT_REPO_REGION
    - ARTIFACT_REPO_ACCESS_KEY_BASE64
    - ARTIFACT_REPO_SECRET_KEY_BASE64
    - KUBEFLOW_ENDPOINT
        - Kubeflow endpoint's URL (i.e. https://kubeflow.exmaple.com) 
    - KUBEFLOW_USERNAME
        - Your Kubeflow username which have right permission to access **staging** tenant
    - KUBEFLOW_PASSWORD
        - Your Kubeflow password which have right permission to access **staging** tenant
    - NAMESPACE
        - Kubeflow profile name(=k8s namespace) where your ML training pipelines run on

- Under **Production** environment
    - ARTIFACT_REPO_REGION
    - ARTIFACT_REPO_ACCESS_KEY_BASE64
    - ARTIFACT_REPO_SECRET_KEY_BASE64
    - KUBEFLOW_ENDPOINT
        - Kubeflow endpoint's URL (i.e. https://kubeflow.exmaple.com) 
    - KUBEFLOW_USERNAME
        - Your Kubeflow username which have right permission to access **staging** tenant
    - KUBEFLOW_PASSWORD
        - Your Kubeflow password which have right permission to access **staging** tenant
    - NAMESPACE
        - Kubeflow profile name(=k8s namespace) where your ML training pipelines run on

## Run workflows
### Model training
1. Commit your code
2. Open a pull request to "development" or "main" branch.
3. Comment on PR as "/train-model"
4. Once bots detect your comment, it builds, deploys, and run a new pipeline version in your training environment
5. Wait for completion of workflow, and check the result

#### notes
- regardless of the branch you request to merge your code, the training pipeline always runs **Training** environment

### Model serving
1. Merge PR to "development" or "main" branch (or directly push to these branches) 
2. Once bots detect that PR has been closed, it starts to deploy a new inference service to your serving enviroment
3. Wait for completion of workflow, and check the result

#### notes
- if you merge to "development", model will be deployed to **Staging** environment
- if you merge to "main", model will be deployed to **Production** environment
- workflow always uses the latest version of model in your artifact repository 