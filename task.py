import json, os, subprocess

input_data = json.load(open('/mnt/work/input/ports.json'))

# required params (will raise Exception if not there)
destination = input_data['destination']  # should be of the form s3://bucket/prefix
access_key_id = input_data['access_key_id']  
secret_key = input_data['secret_key']  

# Optional param.  Temp creds will contain a session token.
session_token = input_data.get('session_token')

os.setenv('AWS_ACCESS_KEY_ID', access_key_id)
os.setenv('AWS_SECRET_ACCESS_KEY',secret_key)
if session_token:
    os.setenv('AWS_SESSION_TOKEN',session_token)

cmd = "aws s3 cp /mnt/work/input/data %s --recursive" % destination

proc = subprocess.Popen([cmd], shell=True)
proc.communicate()
returncode = proc.wait()
if returncode != 0:
    raise Exception('Unable to copy files.')