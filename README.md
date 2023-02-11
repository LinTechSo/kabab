## kabab
kibana backup  (simple script for backup kibana saved objects)

This simple script automate the process of exporting your kibana saved objects (includes index pattern, dashboards, etc) located at `Stack Management > Saved Objects.`

needs s3 credentials and your kibana credentials.

using kibana API below call request:
`POST <kibana host>:<port>/s/<space_id>/api/saved_objects/_export`


