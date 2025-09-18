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
from biobb_dna.stiffness.basepair_stiffness import BPStiffness  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_filename_shift=FILE_IN, input_filename_slide=FILE_IN, input_filename_rise=FILE_IN, input_filename_tilt=FILE_IN, input_filename_roll=FILE_IN, input_filename_twist=FILE_IN, output_csv_path=FILE_OUT, output_jpg_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _bpstiffness(input_filename_shift, input_filename_slide, input_filename_rise, input_filename_tilt, input_filename_roll, input_filename_twist, output_csv_path, output_jpg_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        BPStiffness(input_filename_shift=input_filename_shift, input_filename_slide=input_filename_slide, input_filename_rise=input_filename_rise, input_filename_tilt=input_filename_tilt, input_filename_roll=input_filename_roll, input_filename_twist=input_filename_twist, output_csv_path=output_csv_path, output_jpg_path=output_jpg_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def basepair_stiffness(input_filename_shift, input_filename_slide, input_filename_rise, input_filename_tilt, input_filename_roll, input_filename_twist, output_csv_path, output_jpg_path, properties=None, **kwargs):

    if (output_csv_path is None or (os.path.exists(output_csv_path) and os.stat(output_csv_path).st_size > 0)) and \
       (output_jpg_path is None or (os.path.exists(output_jpg_path) and os.stat(output_jpg_path).st_size > 0)) and \
       True:
        print("WARN: Task BPStiffness already executed.")
    else:
        _bpstiffness( input_filename_shift,  input_filename_slide,  input_filename_rise,  input_filename_tilt,  input_filename_roll,  input_filename_twist,  output_csv_path,  output_jpg_path,  properties, **kwargs)