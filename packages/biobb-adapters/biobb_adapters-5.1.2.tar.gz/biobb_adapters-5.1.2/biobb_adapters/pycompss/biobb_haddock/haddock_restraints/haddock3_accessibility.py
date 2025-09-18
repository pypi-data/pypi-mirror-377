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
from biobb_haddock.haddock_restraints.haddock3_accessibility import Haddock3Accessibility  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, output_accessibility_path=FILE_OUT, output_actpass_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _haddock3accessibility(input_pdb_path, output_accessibility_path, output_actpass_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Haddock3Accessibility(input_pdb_path=input_pdb_path, output_accessibility_path=output_accessibility_path, output_actpass_path=output_actpass_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def haddock3_accessibility(input_pdb_path, output_accessibility_path, output_actpass_path=None, properties=None, **kwargs):

    if (output_accessibility_path is None or (os.path.exists(output_accessibility_path) and os.stat(output_accessibility_path).st_size > 0)) and \
       (output_actpass_path is None or (os.path.exists(output_actpass_path) and os.stat(output_actpass_path).st_size > 0)) and \
       True:
        print("WARN: Task Haddock3Accessibility already executed.")
    else:
        _haddock3accessibility( input_pdb_path,  output_accessibility_path,  output_actpass_path,  properties, **kwargs)