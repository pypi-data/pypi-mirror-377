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
from biobb_dna.curvesplus.canal_unzip import CanalUnzip  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_zip_file=FILE_IN, output_path=FILE_OUT, output_list_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _canalunzip(input_zip_file, output_path, output_list_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CanalUnzip(input_zip_file=input_zip_file, output_path=output_path, output_list_path=output_list_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def canal_unzip(input_zip_file, output_path, output_list_path=None, properties=None, **kwargs):

    if (output_path is None or (os.path.exists(output_path) and os.stat(output_path).st_size > 0)) and \
       (output_list_path is None or (os.path.exists(output_list_path) and os.stat(output_list_path).st_size > 0)) and \
       True:
        print("WARN: Task CanalUnzip already executed.")
    else:
        _canalunzip( input_zip_file,  output_path,  output_list_path,  properties, **kwargs)