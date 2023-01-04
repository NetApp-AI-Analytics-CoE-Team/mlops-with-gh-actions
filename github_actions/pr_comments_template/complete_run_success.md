## :pushpin: Actions Result - Result of ML Pipeline Run"
white_check_mark: Pipeline RUN (ID: ${{ needs.initiate-model-training-run.outputs.run_id }}) has been successfully completed.

## :brain: Model information"
Model package is stored in the artifact repository. 

Artifact URI: ${{ steps.output_model_uri.outputs.model_uri }}

## :mag: How to reproduce the model
To reproduce this model, you can create a Jupyter Workspace which contains source code, hyper parameters, and dataset version by performing following tasks

1. Login to workstation which can access to k8s API
2. Restore dataset version by using NetApp DataOps Toolkit

```bash
# Install NetApp DeepOps Toolkit
$ python3 -m pip install netapp-deepops-k8s

# Clone PVC from snapshot that was taken at model training
$ netapp_dataops_k8s_cli.py clone volume --namespace=${{ needs.initiate-model-training-run.outputs.kubeflow_profile }} --source-snapshot-name=${{ steps.output_dataset_version.outputs.dataset_version }} --new-pvc-name=clone-${{ steps.output_dataset_version.outputs.dataset_version }}
```

3. Create Jupyter workspace with cloned PVC by using NetApp DataOps Toolkit

```
# Create Jupyter Workspace
$ netapp_dataops_k8s_cli.py create jupyterlab --namespace=${{ needs.initiate-model-training-run.outputs.kubeflow_profile }} --workspace-name=reproduce-${{ needs.initiate-model-training-run.outputs.run_id }} --size=10Gi --mount-pvc=clone-${{ steps.output_dataset_version.outputs.dataset_version }} --nvidia-gpu=1
```

4. Connect the workspace provisioned by NetApp DataOps Tooklkit
You can find Workspace URL in result of `netapp_dataops_k8s_cli.py create jupyterlab` command.

5. Resotre the source code and hyper parameters from GitHub commit
```bash
# Open a terminal in Jupyter Workspace and execute below commandlines
$ git clone ${{ context.repo.repo }} .
$ git reset -hard ${{ needs.initiate-model-training-run.outputs.commit_sha }}
```