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
from biobb_flexserv.pcasuite.pcz_unzip import PCZunzip  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pcz_path=FILE_IN, output_crd_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pczunzip(input_pcz_path, output_crd_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        PCZunzip(input_pcz_path=input_pcz_path, output_crd_path=output_crd_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pcz_unzip(input_pcz_path, output_crd_path, properties=None, **kwargs):

    if (output_crd_path is None or (os.path.exists(output_crd_path) and os.stat(output_crd_path).st_size > 0)) and \
       True:
        print("WARN: Task PCZunzip already executed.")
    else:
        _pczunzip( input_pcz_path,  output_crd_path,  properties, **kwargs)