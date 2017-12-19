import json, os, subprocess, shlex, time

input_data = json.load(open('/mnt/work/input/ports.json'))

# required params (will raise Exception if not there)
destination = input_data['destination']  # should be of the form s3://bucket/prefix
access_key_id = input_data['access_key_id']  
secret_key = input_data['secret_key']  

# Optional param.  Temp creds will contain a session token.
session_token = input_data.get('session_token')

os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
if session_token:
    os.environ['AWS_SESSION_TOKEN'] = session_token

cmd = "aws s3 cp /mnt/work/input/data %s --recursive" % destination

retry_counter = 0
while retry_counter < 3:
    try:
        subprocess.check_call(shlex.split(cmd))
        break
    except Exception as ex:
        print("Attempt {_ct} of 3 aws s3 cp for /mnt/work/input/data failed. Error {_e}.".format(
                        _ct=retry_counter+1,
                        _e=str(ex)))
        if retry_counter+1 < 3:
            time.sleep(120)
    finally:
        retry_counter += 1

if retry_counter >= 3:
    raise Exception("Copy failed: Fatal, not retrying")