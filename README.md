## kabab
kibana backup  (simple script for backup kibana saved objects)

This simple script automate the process of exporting your kibana saved objects per space (include index pattern, dashboards, etc) located at `Stack Management > Saved Objects` and upload them into the Minio S3 storage

Needs s3 credentials and your kibana credentials.

Using kibana API request:
`POST <kibana host>:<port>/s/<space_id>/api/saved_objects/_export`

For quick start you can create a docker image from Dockerfile and use the image in `job.yaml` k8s manifest to run this process as a kubernetes job

