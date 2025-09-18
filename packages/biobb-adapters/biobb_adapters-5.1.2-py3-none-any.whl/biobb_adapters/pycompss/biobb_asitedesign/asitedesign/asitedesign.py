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
from biobb_asitedesign.asitedesign.asitedesign import Asitedesign  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb=FILE_IN, input_yaml=FILE_IN, params_folder=FILE_IN, output_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _asitedesign(input_pdb, input_yaml, params_folder, output_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Asitedesign(input_pdb=input_pdb, input_yaml=input_yaml, params_folder=params_folder, output_path=output_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def asitedesign(input_pdb, input_yaml, params_folder, output_path, properties=None, **kwargs):

    if (output_path is None or (os.path.exists(output_path) and os.stat(output_path).st_size > 0)) and \
       True:
        print("WARN: Task Asitedesign already executed.")
    else:
        _asitedesign( input_pdb,  input_yaml,  params_folder,  output_path,  properties, **kwargs)