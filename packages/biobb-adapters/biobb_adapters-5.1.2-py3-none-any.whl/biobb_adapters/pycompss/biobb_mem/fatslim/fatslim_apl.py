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
from biobb_mem.fatslim.fatslim_apl import FatslimAPL  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_path=FILE_IN, output_csv_path=FILE_OUT, input_traj_path=FILE_IN, input_ndx_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _fatslimapl(input_top_path, output_csv_path, input_traj_path, input_ndx_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        FatslimAPL(input_top_path=input_top_path, output_csv_path=output_csv_path, input_traj_path=input_traj_path, input_ndx_path=input_ndx_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def fatslim_apl(input_top_path, output_csv_path, input_traj_path=None, input_ndx_path=None, properties=None, **kwargs):

    if (output_csv_path is None or (os.path.exists(output_csv_path) and os.stat(output_csv_path).st_size > 0)) and \
       True:
        print("WARN: Task FatslimAPL already executed.")
    else:
        _fatslimapl( input_top_path,  output_csv_path,  input_traj_path,  input_ndx_path,  properties, **kwargs)