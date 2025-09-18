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
from biobb_dna.curvesplus.biobb_canal import Canal  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_cda_file=FILE_IN, output_zip_path=FILE_OUT, input_lis_file=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _canal(input_cda_file, output_zip_path, input_lis_file,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Canal(input_cda_file=input_cda_file, output_zip_path=output_zip_path, input_lis_file=input_lis_file, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def biobb_canal(input_cda_file, output_zip_path, input_lis_file=None, properties=None, **kwargs):

    if (output_zip_path is None or (os.path.exists(output_zip_path) and os.stat(output_zip_path).st_size > 0)) and \
       True:
        print("WARN: Task Canal already executed.")
    else:
        _canal( input_cda_file,  output_zip_path,  input_lis_file,  properties, **kwargs)