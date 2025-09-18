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
from biobb_haddock.haddock.capri_eval import CapriEval  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_haddock_wf_data_zip=FILE_IN, output_evaluation_zip_path=FILE_OUT, reference_pdb_path=FILE_IN, output_haddock_wf_data_zip=FILE_OUT, haddock_config_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _caprieval(input_haddock_wf_data_zip, output_evaluation_zip_path, reference_pdb_path, output_haddock_wf_data_zip, haddock_config_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CapriEval(input_haddock_wf_data_zip=input_haddock_wf_data_zip, output_evaluation_zip_path=output_evaluation_zip_path, reference_pdb_path=reference_pdb_path, output_haddock_wf_data_zip=output_haddock_wf_data_zip, haddock_config_path=haddock_config_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def capri_eval(input_haddock_wf_data_zip, output_evaluation_zip_path, reference_pdb_path=None, output_haddock_wf_data_zip=None, haddock_config_path=None, properties=None, **kwargs):

    if (output_evaluation_zip_path is None or (os.path.exists(output_evaluation_zip_path) and os.stat(output_evaluation_zip_path).st_size > 0)) and \
       (output_haddock_wf_data_zip is None or (os.path.exists(output_haddock_wf_data_zip) and os.stat(output_haddock_wf_data_zip).st_size > 0)) and \
       True:
        print("WARN: Task CapriEval already executed.")
    else:
        _caprieval( input_haddock_wf_data_zip,  output_evaluation_zip_path,  reference_pdb_path,  output_haddock_wf_data_zip,  haddock_config_path,  properties, **kwargs)