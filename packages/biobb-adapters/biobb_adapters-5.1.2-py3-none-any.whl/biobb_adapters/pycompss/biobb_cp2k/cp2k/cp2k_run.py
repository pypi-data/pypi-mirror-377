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
from biobb_cp2k.cp2k.cp2k_run import Cp2kRun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_inp_path=FILE_IN, output_log_path=FILE_OUT, output_outzip_path=FILE_OUT, output_rst_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _cp2krun(input_inp_path, output_log_path, output_outzip_path, output_rst_path,  properties, **kwargs):
    
    task_config.config_multinode(properties)
    
    try:
        Cp2kRun(input_inp_path=input_inp_path, output_log_path=output_log_path, output_outzip_path=output_outzip_path, output_rst_path=output_rst_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cp2k_run(input_inp_path, output_log_path, output_outzip_path, output_rst_path, properties=None, **kwargs):

    if (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_outzip_path is None or (os.path.exists(output_outzip_path) and os.stat(output_outzip_path).st_size > 0)) and \
       (output_rst_path is None or (os.path.exists(output_rst_path) and os.stat(output_rst_path).st_size > 0)) and \
       True:
        print("WARN: Task Cp2kRun already executed.")
    else:
        _cp2krun( input_inp_path,  output_log_path,  output_outzip_path,  output_rst_path,  properties, **kwargs)