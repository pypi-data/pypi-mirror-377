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
from biobb_analysis.ambertools.cpptraj_rmsf import CpptrajRmsf  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_path=FILE_IN, input_traj_path=FILE_IN, output_cpptraj_path=FILE_OUT, input_exp_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _cpptrajrmsf(input_top_path, input_traj_path, output_cpptraj_path, input_exp_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CpptrajRmsf(input_top_path=input_top_path, input_traj_path=input_traj_path, output_cpptraj_path=output_cpptraj_path, input_exp_path=input_exp_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cpptraj_rmsf(input_top_path, input_traj_path, output_cpptraj_path, input_exp_path=None, properties=None, **kwargs):

    if (output_cpptraj_path is None or (os.path.exists(output_cpptraj_path) and os.stat(output_cpptraj_path).st_size > 0)) and \
       True:
        print("WARN: Task CpptrajRmsf already executed.")
    else:
        _cpptrajrmsf( input_top_path,  input_traj_path,  output_cpptraj_path,  input_exp_path,  properties, **kwargs)