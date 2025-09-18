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
from biobb_flexdyn.flexdyn.imod_imc import imod_imc  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, input_dat_path=FILE_IN, output_traj_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _imod_imc(input_pdb_path, input_dat_path, output_traj_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        imod_imc(input_pdb_path=input_pdb_path, input_dat_path=input_dat_path, output_traj_path=output_traj_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def imod_imc(input_pdb_path, input_dat_path, output_traj_path, properties=None, **kwargs):

    if (output_traj_path is None or (os.path.exists(output_traj_path) and os.stat(output_traj_path).st_size > 0)) and \
       True:
        print("WARN: Task imod_imc already executed.")
    else:
        _imod_imc( input_pdb_path,  input_dat_path,  output_traj_path,  properties, **kwargs)