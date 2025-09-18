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
from biobb_dna.intrabp_correlations.intrabpcorr import IntraBasePairCorrelation  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_filename_shear=FILE_IN, input_filename_stretch=FILE_IN, input_filename_stagger=FILE_IN, input_filename_buckle=FILE_IN, input_filename_propel=FILE_IN, input_filename_opening=FILE_IN, output_csv_path=FILE_OUT, output_jpg_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _intrabasepaircorrelation(input_filename_shear, input_filename_stretch, input_filename_stagger, input_filename_buckle, input_filename_propel, input_filename_opening, output_csv_path, output_jpg_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        IntraBasePairCorrelation(input_filename_shear=input_filename_shear, input_filename_stretch=input_filename_stretch, input_filename_stagger=input_filename_stagger, input_filename_buckle=input_filename_buckle, input_filename_propel=input_filename_propel, input_filename_opening=input_filename_opening, output_csv_path=output_csv_path, output_jpg_path=output_jpg_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def intrabpcorr(input_filename_shear, input_filename_stretch, input_filename_stagger, input_filename_buckle, input_filename_propel, input_filename_opening, output_csv_path, output_jpg_path, properties=None, **kwargs):

    if (output_csv_path is None or (os.path.exists(output_csv_path) and os.stat(output_csv_path).st_size > 0)) and \
       (output_jpg_path is None or (os.path.exists(output_jpg_path) and os.stat(output_jpg_path).st_size > 0)) and \
       True:
        print("WARN: Task IntraBasePairCorrelation already executed.")
    else:
        _intrabasepaircorrelation( input_filename_shear,  input_filename_stretch,  input_filename_stagger,  input_filename_buckle,  input_filename_propel,  input_filename_opening,  output_csv_path,  output_jpg_path,  properties, **kwargs)