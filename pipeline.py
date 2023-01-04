"""
Demonstration of MLOps pipeline with NetApp DataOps Toolkit
"""
import kfp
from kfp.components import create_component_from_func
import kfp.dsl as dsl
import kfp.onprem as onprem
import sys

"""
Import re-usable components
"""
# Snapshot
from pipeline_components import netapp_snapshot
create_snapshot_op = create_component_from_func(
  netapp_snapshot.create_snapshot,
  base_image="kyonsy0722/netapp-dataops:1.0"
  )

# Train model
from pipeline_components import train_model
train_model_op = create_component_from_func(
  train_model.transfer_learning,
  base_image="tensorflow/tensorflow:2.11.0-gpu",
  packages_to_install=["tensorflow_hub"]
  )

# Upload artifact
from pipeline_components import upload_artifact
upload_artifact_op = create_component_from_func(
  upload_artifact.upload_savedmodel,
  base_image="python:3-slim",
  packages_to_install=["boto3"]
  )


"""
Building pipeline DAG
""" 
@dsl.pipeline(
  name="flower-image-classifier",
  description="Template for executing an AI training run with built-in training dataset traceability and trained model versioning",
)
def ai_training_run(
  # Define pipeline parameters
  dataset_pvc_name: str="dataset-flower",
  # model_pvc_name: str="model",
  kubeflow_user_namespace: str="kubeflow-user-example-com",
  volume_snapshot_class :str="csi-snapclass",
  # train_step_num_gpu:int=1,
  batch_size:int=16,
  epochs:int=5,
  learning_rate:float=0.005,
  momentum:float=0.9,
  label_smoothing:float=0.1,
  dropout_rate:float=0.2
):
  DATASET_DIR = "/mnt/dataset"
  SNAPSHOT_NAME = f"{dataset_pvc_name}-{kfp.dsl.RUN_ID_PLACEHOLDER}"
  MODEL_NAME = "flower-classifier"
  MODEL_METADATA = {
    "x-amz-meta-NAMESPACE-TRAINED-AT": kubeflow_user_namespace,
    "x-amz-meta-DATASET-PVC-NAME": dataset_pvc_name,
    "x-amz-meta-DATASET-VERSION-NAME": SNAPSHOT_NAME,
    "x-amz-meta-KFP-RUN-ID": kfp.dsl.RUN_ID_PLACEHOLDER
  }
  TRAIN_STEP_NUM_GPU = 1

  # STEP1: Taking snapshot before training 
  snapshot_before_training = create_snapshot_op(
    namespace=kubeflow_user_namespace, 
    pvc_name=dataset_pvc_name, 
    snapshot_name=SNAPSHOT_NAME,
    volume_snapshot_class=volume_snapshot_class
    ).set_display_name('Dataset snapshoter').set_caching_options(enable_caching=False)

  # STEP2: Training model
  train_task = train_model_op(
    model_name=MODEL_NAME,
    data_dir=DATASET_DIR,
    batch_size=batch_size,
    epochs=epochs,
    learning_rate=learning_rate,
    momentum=momentum,
    label_smoothing=label_smoothing,
    dropout_rate=dropout_rate
    ).after(snapshot_before_training).set_display_name('Model trainer').set_caching_options(enable_caching=False)

  # mount dataset PVC
  train_task.apply(
    onprem.mount_pvc(dataset_pvc_name, 'datavol', DATASET_DIR)
  )
  # set gpu limit
  if TRAIN_STEP_NUM_GPU > 0:
    train_task.set_gpu_limit(TRAIN_STEP_NUM_GPU, 'nvidia')

  # STEP3: Update model to artifact repository
  upload_task = upload_artifact_op(
    input_model = train_task.outputs["output_model"],
    archive_name = kfp.dsl.RUN_ID_PLACEHOLDER, # use RUN ID as s3 object name
    model_name = MODEL_NAME,
    object_metadata = MODEL_METADATA
    ).set_display_name('Artifact uploader').set_caching_options(enable_caching=False)
  # pass s3 credentials to the task
  upload_task.apply(
    onprem.use_k8s_secret(
      secret_name='s3-secret-artifact',
      k8s_secret_key_to_env={
          's3_secret_key': 'AWS_SECRET_ACCESS_KEY',
          's3_access_key': 'AWS_ACCESS_KEY',
          's3_region': 'AWS_REGION',
          's3_bucket_name': 'AWS_BUCKET_NAME'
          }))

"""
Compile a pipeline
"""
if __name__ == "__main__":
  if len(sys.argv) == 2:
    kfp.compiler.Compiler().compile(
        pipeline_func=ai_training_run,
        package_path=sys.argv[1])
  else:
    print("Usage: python3 FILE_NAME.py <PIPELINE_PACKAGE_PATH>")
    sys.exit(1)