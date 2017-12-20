# gbdx-task-StageDataToS3
The SaveToS3 task that runs in GBDX: for pushing output data to S3.

# Simple example:
```python
from gbdxtools import Interface
gbdx = Interface()

savedata = gbdx.Task('SaveToS3')
savedata.inputs.destination = 's3://your-bucket/somewhere_nice'
savedata.inputs.access_key_id = '<your-s3-access-key>'
savedata.inputs.secret_key = '<your-s3-secret-key>'
savedata.inputs.session_token = '<your-optional-session-token-if-these-are-temporary-creds>'
savedata.inputs.data = 'some-input-data-from-s3-or-another-task-output'

wf = gbdx.Workflow([savedata])
wf.execute()
```