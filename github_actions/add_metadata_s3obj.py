import boto3
import argparse
import sys

def add_metadata_to_s3_object(
    s3_uri: str,
    metadata_key: str,
    metadata_value: str
):

    # get bucket name and file path from s3 uri
    # s3 uri would be s3://bucket_name/file_path
    s = s3_uri.replace('s3://', '')
    s_split = s.split('/', 1)

    bucket_name = s_split[0]
    file_path = s_split[1]

    try:
        client = boto3.client('s3')
        # get existing object 
        obj = client.get_object(Bucket=bucket_name, Key=file_path)
        # get existing metadata
        httpHeaders = obj["ResponseMetadata"]["HTTPHeaders"]
        contentType = obj["ContentType"]
        metadata = obj["Metadata"]

        # create new metadata
        metadata[metadata_key] = metadata_value
        
        # replace obj
        client.copy_object(Key=file_path, Bucket=bucket_name,
                                CopySource={
                                    "Bucket": bucket_name, "Key": file_path},
                                Metadata=metadata,
                                ContentType=contentType,
                                MetadataDirective="REPLACE"
                                )
        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-uri', help="s3 uri that stores model archive", required=True)
    parser.add_argument('--metadata-key', help="metadata key that applyed to s3 object", required=True)
    parser.add_argument('--metadata-value', help="metadata key that applyed to s3 object", required=True)
    args = parser.parse_args()

    ret = add_metadata_to_s3_object(
        s3_uri = args.model_uri,
        metadata_key = args.metadata_key,
        metadata_value = args.metadata_value
    )

    if ret:
        sys.exit(0)
    else:
        sys.exit(1)