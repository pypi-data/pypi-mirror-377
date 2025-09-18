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
from biobb_haddock.haddock_restraints.haddock3_passive_from_active import Haddock3PassiveFromActive  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, output_actpass_path=FILE_OUT, input_active_list_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _haddock3passivefromactive(input_pdb_path, output_actpass_path, input_active_list_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Haddock3PassiveFromActive(input_pdb_path=input_pdb_path, output_actpass_path=output_actpass_path, input_active_list_path=input_active_list_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def haddock3_passive_from_active(input_pdb_path, output_actpass_path, input_active_list_path=None, properties=None, **kwargs):

    if (output_actpass_path is None or (os.path.exists(output_actpass_path) and os.stat(output_actpass_path).st_size > 0)) and \
       True:
        print("WARN: Task Haddock3PassiveFromActive already executed.")
    else:
        _haddock3passivefromactive( input_pdb_path,  output_actpass_path,  input_active_list_path,  properties, **kwargs)