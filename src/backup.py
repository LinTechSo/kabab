import json
import base64
import os
import time
import boto3
import requests

import glog as log

def authorization(kibana_username, kibana_password):
    usrPass = f"{kibana_username}:{kibana_password}"
    b64Val = base64.b64encode(str(usrPass).encode())
    
    return b64Val


def aws_connection(s3_endpoint, s3_access_key_id, s3_secret_access_key):
    s3 = boto3.resource('s3', 
    endpoint_url=f'{s3_endpoint}',
    aws_access_key_id=f'{s3_access_key_id}',
    aws_secret_access_key=f'{s3_secret_access_key}',
    config=boto3.session.Config(signature_version='s3v4')
    )
    
    return s3

def put_object(
        data, 
        s3_endpoint, 
        s3_access_key_id,
        s3_secret_access_key,
        s3_bucket, 
        kibana_space
        ):
    
    try:
        s3 = aws_connection(s3_endpoint, s3_access_key_id, s3_secret_access_key)
        str_date_time = time.strftime("%d-%m-%Y-%H-%M-%S")
        
        s3object = s3.Object(
            f'{s3_bucket}', f'backup-{kibana_space}-{str_date_time}.ndjson'
            )
    
        s3object.put(
            Body=(eval(json.dumps(data)))
        )
        
        log.info(f'Backup from {kibana_space} on {str_date_time} has completed')
    
    except:
        log.error(f'Backup from {kibana_space} on {str_date_time} has failed ')
    
    
def export(
        kibana_endpoint, 
        kibana_space, 
        kibana_username, 
        kibana_password, 
        s3_endpoint, 
        s3_access_key_id, 
        s3_secret_access_key,
        s3_bucket,              
        ):

    b64Val = authorization(kibana_username, kibana_password).decode()
    
    url = f"{kibana_endpoint}/s/{kibana_space}/api/saved_objects/_export"
    
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

    put_object(response.text, 
               s3_endpoint, 
               s3_access_key_id,
               s3_secret_access_key,
               s3_bucket,
               kibana_space,
               ) 
        
    return_info = {"Job": "Completed"}
    return json.dumps(return_info)

def logic():
    
    try:
        kibana_endpoint = os.getenv('KIBANA_ENDPOINT')
        kibana_space = os.getenv('KIBANA_SPACE')
        kibana_username = os.getenv('KIBANA_USERNAME')
        kibana_password = os.getenv('KIBANA_PASSWORD')
    except:
        log.error(f'Error in reading Kibana environment variables')
        
    try:
        s3_endpoint = os.getenv('AWS_ENDPOINT')
        s3_access_key_id = os.getenv('AWS_ACCESS_KEY')
        s3_secret_access_key = os.getenv('AWS_ACCESS_PASSWORD')
        s3_bucket = os.getenv('AWS_BUCKET')
    except:
         log.error(f'Error in reading S3 environment variables')

    result = export(
            kibana_endpoint, 
            kibana_space, 
            kibana_username, 
            kibana_password, 
            s3_endpoint, 
            s3_access_key_id, 
            s3_secret_access_key,
            s3_bucket,
            )
    
    log.info(f'{result}')

if __name__ == "__main__":
    logic()
