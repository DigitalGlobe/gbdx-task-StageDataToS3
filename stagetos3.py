import os
import subprocess
import logging
import urlparse
import shutil
import json
logger = logging.getLogger('{name}'.format(name=os.path.basename(str(__file__)).replace(".py", "")))
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('{name}.log'.format(name=str(__file__).replace(".py", "")))
handler.name = logger.name
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

from common import JobRunner


class Stagetos3Runner(JobRunner):
    """A job runner that will do something.

    Attributes:
      invoke:
    """
    __input_port_name = "data"
    __exe = 'aws s3 cp'

    def __init__(self, work_path="/mnt/work/"):
        super(Stagetos3Runner, self).__init__(work_path=work_path)

    @property
    def destination(self):
        """
        S3 destination bucket and keypath
        :return:
        """
        dest = self.get_input_string_port("destination")
        if not dest:
            raise RuntimeError("stagetos3::destination => input string port 'destination' must be provided.")
        return dest

    def invoke(self):
        """
        Run the action job and figure out where input and output should be task signature.
        """
        this_input_dir = self.get_input_data_port(self.__input_port_name)
        # for everything in the collection now actually run the processes
        logger.info("Executing processes")

        parsed = urlparse.urlparse(self.destination)
        host = str(parsed.netloc).replace(".s3.amazonaws.com", "")
        output_destination = "{_scheme}://{_host}{_path}".format(_scheme='s3', _host=host, _path=parsed.path)

        # do copy
        args = "{exe} {input} {output} --recursive".format(exe=self.__exe, input=this_input_dir, output=output_destination)

        logger.info("Command Line: {_args}".format(_args=args))
        proc = subprocess.Popen([args], shell=True)
        proc.communicate()
        returncode = proc.wait()
        logger.info("Return code: {_args}".format(_args=returncode))
        if returncode != 0:
            raise Exception("{exe} for {path} failed.".format(exe=self.__exe, path=this_input_dir))

        logger.info("Invoke complete")

        try:
            shutil.copyfile(handler.baseFilename, os.path.join(self.base_path, os.path.basename(handler.baseFilename)))
        except Exception as ex:
            logger.warn("Failed to copy log file to output. Error: {_e}".format(_e=ex))

        return True

    @staticmethod
    def get_signature():
        return {'inputs': ['data', 'ports.json'], 'outputs': []}

if __name__ == "__main__":
    logger.info('Welcome to {name}'.format(name=os.path.basename(str(__file__))))
    logger.info('Task signature is:\n {_sig}'.format(_sig=json.dumps(Stagetos3Runner.get_signature(), indent=4)))
    retval = False
    message = ""
    runner = None
    try:
        runner = Stagetos3Runner()
        retval = runner.invoke()
    except Exception as e:
        logger.error(str(e))
        message = str(e)
    finally:
        if runner:
            runner.finalize('success' if retval is True else 'failed', message)
        logger.info("Return code => {_retval}".format(_retval=int(retval) - 1))
        if len(message) > 0:
            logger.info("Message => {_message}".format(_message=message))
