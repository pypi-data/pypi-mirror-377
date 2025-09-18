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
from biobb_dna.dna.dna_timeseries_unzip import DnaTimeseriesUnzip  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_zip_file=FILE_IN, output_path_csv=FILE_OUT, output_path_jpg=FILE_OUT, output_list_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _dnatimeseriesunzip(input_zip_file, output_path_csv, output_path_jpg, output_list_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        DnaTimeseriesUnzip(input_zip_file=input_zip_file, output_path_csv=output_path_csv, output_path_jpg=output_path_jpg, output_list_path=output_list_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def dna_timeseries_unzip(input_zip_file, output_path_csv, output_path_jpg, output_list_path=None, properties=None, **kwargs):

    if (output_path_csv is None or (os.path.exists(output_path_csv) and os.stat(output_path_csv).st_size > 0)) and \
       (output_path_jpg is None or (os.path.exists(output_path_jpg) and os.stat(output_path_jpg).st_size > 0)) and \
       (output_list_path is None or (os.path.exists(output_list_path) and os.stat(output_list_path).st_size > 0)) and \
       True:
        print("WARN: Task DnaTimeseriesUnzip already executed.")
    else:
        _dnatimeseriesunzip( input_zip_file,  output_path_csv,  output_path_jpg,  output_list_path,  properties, **kwargs)