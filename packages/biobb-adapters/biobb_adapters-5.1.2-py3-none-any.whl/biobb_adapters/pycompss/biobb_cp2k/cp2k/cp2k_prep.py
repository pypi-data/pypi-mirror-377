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
from biobb_cp2k.cp2k.cp2k_prep import Cp2kPrep  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_inp_path=FILE_OUT, input_inp_path=FILE_IN, input_pdb_path=FILE_IN, input_rst_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _cp2kprep(output_inp_path, input_inp_path, input_pdb_path, input_rst_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Cp2kPrep(output_inp_path=output_inp_path, input_inp_path=input_inp_path, input_pdb_path=input_pdb_path, input_rst_path=input_rst_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cp2k_prep(output_inp_path, input_inp_path=None, input_pdb_path=None, input_rst_path=None, properties=None, **kwargs):

    if (output_inp_path is None or (os.path.exists(output_inp_path) and os.stat(output_inp_path).st_size > 0)) and \
       True:
        print("WARN: Task Cp2kPrep already executed.")
    else:
        _cp2kprep( output_inp_path,  input_inp_path,  input_pdb_path,  input_rst_path,  properties, **kwargs)