# Python
import os
import sys
import traceback
# Pycompss
from pycompss.api.task import task
from pycompss.api.parameter import FILE_IN, FILE_OUT
# Adapters commons pycompss
from biobb_adapters.pycompss.biobb_commons import task_config
# Wrapped Biobb
from biobb_pdb_tools.pdb_tools.biobb_pdb_splitseg import Pdbsplitseg  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_file_path=FILE_IN, output_file_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pdbsplitseg(input_file_path, output_file_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Pdbsplitseg(input_file_path=input_file_path, output_file_path=output_file_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def biobb_pdb_splitseg(input_file_path, output_file_path, properties=None, **kwargs):

    if (output_file_path is None or (os.path.exists(output_file_path) and os.stat(output_file_path).st_size > 0)) and \
       True:
        print("WARN: Task Pdbsplitseg already executed.")
    else:
        _pdbsplitseg( input_file_path,  output_file_path,  properties, **kwargs)