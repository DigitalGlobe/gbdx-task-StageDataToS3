import os
import inspect
import fnmatch
import json


########################################################################################################################
#
# Job runner base class
#
########################################################################################################################
class JobRunner(object):
    """A job runner base class.
    NOTE: only use input_path and output_path if you really want to read/write something that is not a port
    """

    def __init__(self, work_path="/mnt/work/"):
        self.__work_path = work_path
        self.__scratch_path = None
        self.__string_ports = None
        self.__test = None

        if not os.path.exists(self.__work_path):
            raise Exception("Working path must exist. {_path}.".format(_path=self.__work_path))

        sports = os.path.join(self.__work_path, 'input', "ports.json")
        if os.path.exists(sports):
            with open(sports, 'r') as f:
                self.__string_ports = json.load(f)

    @property
    def base_path(self):
        return self.__work_path

    @property
    def input_path(self):
        return os.path.join(self.base_path, 'input')

    @property
    def output_path(self):
        return os.path.join(self.base_path, 'output')

    @property
    def scratch_path(self):
        return os.path.join(self.base_path, 'scratch')

    def get_input_string_port(self, port_name, default=None):
        """
        Get input string port value
        :param port_name:
        :param default:
        :return: :rtype:
        """
        if self.__string_ports:
            return self.__string_ports.get(port_name, default)
        return default

    def get_input_data_port(self, port_name):
        """
        Get the input location for a specific port
        :param port_name:
        :return: :rtype:
        """
        return os.path.join(self.input_path, port_name)

    def get_output_data_port(self, port_name):
        """
        Get the output location for a specific port
        :param port_name:
        :return: :rtype:
        """
        return os.path.join(self.output_path, port_name)

    def get_scratch_path(self, port_name, createifnotexist=True):
        """
        Get the temp scratch path.
        :return:
        """
        spath = os.path.join(self.scratch_path, port_name)
        if createifnotexist and not os.path.exists(spath):
            os.makedirs(spath)

        return spath

    @property
    def test(self):
        """
        Is this running as part of a unittest
        :return: :rtype:
        """
        if self.__test:
            return True
        return False

    @test.setter
    def test(self, value):
        """
        Set that this is running as part of a unittest and therefor don't run the actual demchip and ortho commands
        :param value:
        """
        self.__test = value

    def invoke(self):
        """
        The do something method

        :rtype : bool
        :raise RuntimeError:
        """
        raise RuntimeError("JobRunner Baseclass invoke is not callable")
        # return False

    def finalize(self, success_or_fail, message):
        """
        :param success_or_fail: string that is 'success' or 'fail'
        :param message:
        """
        with open(os.path.join(self.base_path, 'status.json'), 'w') as f:
            json.dump({'status': success_or_fail, 'reason': message}, f, indent=4)

    def collate_and_write_lineage(self, lineage_dict, input_dir, output_dir):
        prevlin = None
        try:
            if os.path.exists(os.path.join(input_dir, 'lineage.json')):
                with open(os.path.join(input_dir, 'lineage.json'), 'r') as fd:
                    prevlin = json.load(fd)
        except Exception as e:
            print(str(e))
        with open(os.path.join(output_dir, 'lineage.json'), 'w') as f:
            if prevlin:
                collated = [prevlin, lineage_dict]
            else:
                collated = lineage_dict
            json.dump(collated, f, indent=4)


class Lineage(object):

    def __init__(self):
        self.__lineage = {"lineage": []}

    def __repr__(self):
        return self.__str__()

    @property
    def lineage(self):
        return self.__lineage

    def __str__(self):
        return json.dumps(self.__lineage)

    def append(self, item):
        """
        Append the item to the lineage
        :param item: this can be a string or another dict
        """
        self.lineage["lineage"].append(item)

    def as_dict(self):
        return self.__lineage


########################################################################################################################
#
# Utility functions
#
########################################################################################################################
def find_files_in_path(path, match="*.*"):
    """
    Get a list of tills in path
    :param path: the fill path to the til file
    :return: an array full paths to tils
    :raise Exception:
    """
    directory = os.path.normpath(os.path.abspath(path))
    retval = []
    try:
        # traverse root directory, and list directories as dirs and files as files
        for dirpath, dirs, files in os.walk(directory):
            for mfile in [n for n in files if fnmatch.fnmatch(str(n).lower(), match.lower())]:
                retval.append(os.path.join(dirpath, mfile))
    except Exception as e:
        raise Exception("common::{_method} Error walking path: {_path}. Error: {_error}".format(_method=inspect.stack()[0][3], _path=directory, _error=str(e)))

    return retval


def find_tiffs_in_til(tilfile):
    """
    Get a list of full paths from til file.
    :param tilfile: the fill path to the til file
    :return: an array of named tuples
    :raise Exception:
    """
    f = None
    try:
        if not os.path.exists(tilfile):
            raise Exception("common::{_method} {_tilfile} does not exist.".format(_method=inspect.stack()[0][3], _tilfile=tilfile))
        f = open(tilfile)
        dirname = os.path.dirname(tilfile)
        tiles = []
        for ln in iter(f):
            if "BEGIN_GROUP = TILE_" in ln.upper():
                filename = None
                while "END_GROUP = TILE_" not in ln.upper():
                    if "filename" in ln.lower():
                        filename = ln.split('=')[-1].strip().strip(';').strip('"')
                    ln = next(f)

                tiles.append(os.path.normpath(os.path.join(dirname, filename)))
    except Exception as e:
        raise Exception("common::{_method} Error parsing til file: {_tilfile}. Error: {_error}".format(_method=inspect.stack()[0][3], _tilfile=tilfile, _error=str(e)))
    finally:
        if f is not None:
            f.close()

    return tiles


####################################################################################
def find_p00_aux(til, auxext=".xml"):
    """
    Based on til try to guess the name of the aux containing all the metadata.
    Note: case insensitive
    :param til:
    :return: :rtype: :raise Exception:
    """
    try:
        targetbase = os.path.splitext(os.path.basename(til))[0]
        path = os.path.dirname(til)
        for root, dirs, files in os.walk(path, topdown=True):
            for f in files:
                base, ext = os.path.splitext(f)
                if str(ext).lower() == auxext.lower():
                    if str(f).lower() == "{_targetbase}{_extn}".format(_targetbase=targetbase, _extn=auxext).lower():
                        return str(os.path.normpath(os.path.join(root, f)))
                    elif targetbase[0:16].lower() in str(f).lower():
                        return str(os.path.normpath(os.path.join(root, f)))
                    else:
                        pass
    except Exception as e:
        msg = "common::{_method} {_err}".format(_method=inspect.stack()[0][3], _err=str(e))
        raise Exception(msg)
