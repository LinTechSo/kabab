import json
import base64
import os
import uuid

from minio import Minio
import requests
import glog as log

def authorization(kibana_username, kibana_password):
    usrPass = f"{kibana_username}:{kibana_password}"
    b64Val = base64.b64encode(str(usrPass).encode())
    
    return b64Val

def export(kibana_url, kibana_space, kibana_username, kibana_password):
    url = f"https://{kibana_url}/s/{kibana_space}/api/saved_objects/_export"

    b64Val = authorization(kibana_username, kibana_password).decode()

    payload = json.dumps({
    "type": [
        "dashboard",
        "index-pattern",
        "config",
        "lens",
        "url",
        "tag",
        "search"
    ]
    })
    headers = {
    'kbn-xsrf': 'true',
    'Content-Type': 'application/json',
    'Authorization': f'Basic {b64Val}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    f = open(f"/app/backup-{kibana_space}.ndjson", "a")
    f.write(response.text)
    f.close()

    return True


def backup(endpoint_url, aws_access_key_id, aws_secret_access_key, bucket, kibana_space):
    s3_client = Minio(endpoint_url,
            access_key=aws_access_key_id,
            secret_key=aws_secret_access_key,
            secure=False
            )
    
    result = f"/app/backup-{kibana_space}.ndjson"
    unique_filename = str(uuid.uuid4())
    
    try:
        s3_client.fput_object(bucket, f"/{kibana_space}/backup-{unique_filename}-{kibana_space}.ndjson", result)
        log.info(f'Backup {kibana_space} in {bucket} has completed')
    except:
        log.error(f'Backup {kibana_space} in {bucket} failed ')


def logic():
    try:
        kibana_url = os.getenv('KIBANA_URL')
        kibana_space = os.getenv('KIBANA_SPACE')
        kibana_username = os.getenv('KIBANA_USERNAME')
        kibana_password = os.getenv('KIBANA_PASSWORD')
        endpoint_url = os.getenv('AWS_ENDPOINT')
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
        aws_secret_access_key = os.getenv('AWS_ACCESS_PASSWORD')
        bucket = os.getenv('AWS_BUCKET')
    except:
         log.error(f'Error in reading environment variables')
    
    if export(kibana_url, kibana_space, kibana_username, kibana_password):    
        log.info(f'Backup is in progress')
        backup(endpoint_url, aws_access_key_id, aws_secret_access_key, bucket, kibana_space)
    
    log.info(f'Done')

if __name__ == "__main__":
    logic()
