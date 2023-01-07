# About this actions
- provide CI/CD/CT pipelines for Machine Learning models.
- provide two workflows

# Prerequisite
- GitHub App
- GitHub Actions Runner
    - kubeconfig that associated with Training and Serving cluster
- K8s Clusters
    - Training
        - Kubeflow (installed as multi user mode)
        - You can use same cluster as both for Training and for Serving 
    - Serving
        - Kubeflow (installed as multi user mode)
        - You can use same cluster as both for Training and for Serving 

# How to use
## Initial Setup
### On your GitHub repository
1. Create enviroments named as below in you GitHub repository
- Training
- Serving


2. Define secrets under each environments as below
- Under "Training" environment
    - K8S_CONTEXT
        - context name that is defined in kubeconfig in your github actions runner
    - KUBEFLOW_ENDPOINT
        - Kubeflow endpoint's URL (i.e. https://kubeflow.exmaple.com) 
    - KUBEFLOW_USERNAME
        - Your Kubeflow username
    - KUBEFLOW_PASSWORD
        - Your Kubeflow password
    - KUBEFLOW_EXPERIMENT_NAME
        - Existing experiment name on your Kubeflow profile
    - NAMESPACE
        - Kubeflow profile name(=k8s namespace) where your ML training pipelines run on
- Under "Serving" environment
    - ARTIFACT_REPO_REGION
    - ARTIFACT_REPO_ACCESS_KEY_BASE64
    - ARTIFACT_REPO_SECRET_KEY_BASE64
    - K8S_CONTEXT
        - context name that is defined in kubeconfig in your github actions runner
    - KUBEFLOW_ENDPOINT
        - Kubeflow endpoint's URL (i.e. https://kubeflow.exmaple.com) 
    - KUBEFLOW_USERNAME
        - Your Kubeflow username
    - KUBEFLOW_PASSWORD
        - Your Kubeflow password
    - KUBEFLOW_EXPERIMENT_NAME
        - Existing experiment name on your Kubeflow profile
    - NAMESPACE
        - Kubeflow profile name(=k8s namespace) where your ML training pipelines run on

## Run workflows

