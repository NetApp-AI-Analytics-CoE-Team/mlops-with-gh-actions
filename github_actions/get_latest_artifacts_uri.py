from boto3 import Session
import sys
import argparse

def get_latest_object_name(
    session: Session,
    s3_bucket: str,
    s3_prefix: str,
) -> None:
    '''
    S3から特定のフォルダ配下の最新ファイルをダウンロードするメソッド。

    Parameters
    ----------
    session: Session
        boto3.sessionオブジェクト。
    s3_bucket: string
        最新ファイルをダウンロードしたいS3バケット名。
    s3_prefix: string
        最新ファイルをダウンロードしたいS3フォルダパス。
    dist_file_path: string
        ダウンロード先のファイルパス。
    '''
    s3 = session.resource("s3")
    bucket = s3.Bucket(s3_bucket)

    # S3から学習済みモデルをダウンロード
    # 学習済みモデルが格納されているS3ディレクトリ内のファイルリストオブジェクトを作成
    objs = bucket.meta.client.list_objects_v2(
        Bucket=bucket.name,
        Prefix=s3_prefix
    )
    # ディレクトリ配下のファイルについてLOOP処理
    # 最新の更新日付のファイルがダウンロードされる
    loop_first_f = True
    for o in objs.get('Contents'):
        # LOOP初回処理
        if loop_first_f:
            download_target_file = o.get('Key')
            modified_datetime_mid = o.get('LastModified')
            loop_first_f = False
        # 2回目以降
        else:
            # 最新の修正日時のファイル名を保持
            if modified_datetime_mid <= o.get('LastModified'):
                modified_datetime_mid = o.get('LastModified')
                download_target_file = o.get('Key')

    # print(f'download target file is: {download_target_file}')
    return download_target_file

if __name__ == '__main__':
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', help="bucket name where the artifacts is stored", required=True)
    parser.add_argument('--prefix', help="prefix to artifact folder", required=True)
    args = parser.parse_args()

    SESSION=Session()
    try:
        ret = get_latest_object_name(SESSION, args.bucket, args.prefix)
        print(f"s3://{args.bucket}/{ret}")
        sys.exit(0)
    except:
        sys.exit(1)
