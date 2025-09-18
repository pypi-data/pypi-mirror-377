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
from biobb_mem.lipyphilic_biobb.lpp_flip_flop import LPPFlipFlop  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_path=FILE_IN, input_traj_path=FILE_IN, input_leaflets_path=FILE_IN, output_flip_flop_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _lppflipflop(input_top_path, input_traj_path, input_leaflets_path, output_flip_flop_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        LPPFlipFlop(input_top_path=input_top_path, input_traj_path=input_traj_path, input_leaflets_path=input_leaflets_path, output_flip_flop_path=output_flip_flop_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def lpp_flip_flop(input_top_path, input_traj_path, input_leaflets_path, output_flip_flop_path, properties=None, **kwargs):

    if (output_flip_flop_path is None or (os.path.exists(output_flip_flop_path) and os.stat(output_flip_flop_path).st_size > 0)) and \
       True:
        print("WARN: Task LPPFlipFlop already executed.")
    else:
        _lppflipflop( input_top_path,  input_traj_path,  input_leaflets_path,  output_flip_flop_path,  properties, **kwargs)