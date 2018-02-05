# gbdx-task-StageDataToS3
The SaveToS3 task that runs in GBDX: for pushing output data to S3.

# Simple Example:
```python
from gbdxtools import Interface
gbdx = Interface()

savedata = gbdx.Task('SaveToS3')
savedata.inputs.destination = 's3://your-bucket/somewhere_nice'
savedata.inputs.access_key_id = '<your-s3-access-key>'
savedata.inputs.secret_key = '<your-s3-secret-key>'
savedata.inputs.session_token = '<your-session-token>'
savedata.inputs.data = 'some-input-data-from-s3-or-another-task-output'

wf = gbdx.Workflow([savedata])
wf.execute()
```


# Example Getting Temp Creds
```
# First we'll run atmospheric compensation on Landsat8 data
from gbdxtools import Interface
gbdx = Interface()

acomp = gbdx.Task('AComp', data='s3://landsat-pds/L8/033/032/LC80330322015035LGN00')

# Now we'll save the result to our own S3 bucket.  First we need to generate temporary AWS credentials
# (this assumes you have an AWS account and your IAM credentials are appropriately accessible via boto:
# env vars or aws config file)
import boto3
client = boto3.client('sts')
response = client.get_session_token(DurationSeconds=86400)
access_key_id = response['Credentials']['AccessKeyId']
secret_key = response['Credentials']['SecretAccessKey']
session_token = response['Credentials']['SessionToken']

# Save the data to your s3 bucket using the SaveToS3 task:
savetask = gbdx.Task('SaveToS3')
savetask.inputs.data = acomp.outputs.data.value
savetask.inputs.destination = "s3://your-bucket/your-path/"
savetask.inputs.access_key_id = access_key_id
savetask.inputs.secret_key = secret_key
savetask.inputs.session_token = session_token

workflow = gbdx.Workflow([acomp, savetask])
workflow.execute()
```
