
from kfp.components import InputPath

#
# upload trained model to AWS S3
#  
def upload_savedmodel(
    # saved_model_dir:str, 
    archive_name:str,
    model_name:str,
    input_model_path:InputPath('model'),
    object_metadata:dict={},
    ) -> str:
    import boto3
    import tarfile
    import os
    ARCHIVE_TEMP_PATH = f"/tmp/{archive_name}.tgz"
    OBJ_KEY = f"{model_name}/{archive_name}.tgz"

    # archive savedmodel directory
    with tarfile.open(name=ARCHIVE_TEMP_PATH, mode="w:gz") as mytar:
        mytar.add(input_model_path, arcname="1")

    # create s3 client
    client = boto3.client(
        's3',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_REGION"],
    )

    # upload artifact archive
    print("uploading artifact to AWS S3...")
    client.upload_file(ARCHIVE_TEMP_PATH, os.environ["AWS_BUCKET_NAME"], OBJ_KEY, ExtraArgs={'Metadata': object_metadata})
    print("upload completed successfully")

    s3_url = f's3://{os.environ["AWS_BUCKET_NAME"]}/{OBJ_KEY}'
    object_url = f'https://{os.environ["AWS_BUCKET_NAME"]}.s3.{os.environ["AWS_REGION"]}.amazonaws.com/{OBJ_KEY}' 
    print(f"object download url is: {object_url}")
    return s3_url