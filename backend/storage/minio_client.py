from minio import Minio

client=Minio('minio:9000',access_key='minioadmin',secret_key='minioadmin',secure=False)

def save(bucket, name, path):
    if not client.bucket_exists(bucket): 
        client.make_bucket(bucket)
    client.fput_object(bucket, name, path)
