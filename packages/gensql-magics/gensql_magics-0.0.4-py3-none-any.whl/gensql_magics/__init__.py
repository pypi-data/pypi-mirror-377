from .magic import GenSQLMagics
import subprocess
from packaging import version
import sys

#__version__ = "0.0.1"

_min_java_version = version.parse("24")

# Load the magic
def load_ipython_extension(ipython):
    ipython.register_magics(GenSQLMagics)
    java_version = version.parse(get_java_version())
    if(java_version < _min_java_version):
        print(f"Need Java version >= {_min_java_version}, found version {java_version}", file=sys.stderr)
        print("This could be a bug in GenSQL's Java detection.", file=sys.stderr)

def get_java_version():
    try:
        result = subprocess.run(['java', '-version'], stderr=subprocess.PIPE, text=True)
        output = result.stderr
        if "version" in output:
            return version.parse(output.splitlines()[0].split('"')[1])
        else:
            return version.parse('0')
    except FileNotFoundError:
        return version.parse('0')
