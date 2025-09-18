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
from biobb_dna.dna.dna_bimodality import HelParBimodality  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_csv_file=FILE_IN, output_csv_path=FILE_OUT, output_jpg_path=FILE_OUT, input_zip_file=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _helparbimodality(input_csv_file, output_csv_path, output_jpg_path, input_zip_file,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        HelParBimodality(input_csv_file=input_csv_file, output_csv_path=output_csv_path, output_jpg_path=output_jpg_path, input_zip_file=input_zip_file, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def dna_bimodality(input_csv_file, output_csv_path, output_jpg_path, input_zip_file=None, properties=None, **kwargs):

    if (output_csv_path is None or (os.path.exists(output_csv_path) and os.stat(output_csv_path).st_size > 0)) and \
       (output_jpg_path is None or (os.path.exists(output_jpg_path) and os.stat(output_jpg_path).st_size > 0)) and \
       True:
        print("WARN: Task HelParBimodality already executed.")
    else:
        _helparbimodality( input_csv_file,  output_csv_path,  output_jpg_path,  input_zip_file,  properties, **kwargs)