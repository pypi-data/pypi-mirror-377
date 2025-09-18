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
from biobb_pytorch.mdae.train_mdae import TrainMDAE  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_train_npy_path=FILE_IN, output_model_pth_path=FILE_OUT, input_model_pth_path=FILE_IN, output_train_data_npz_path=FILE_OUT, output_performance_npz_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _trainmdae(input_train_npy_path, output_model_pth_path, input_model_pth_path, output_train_data_npz_path, output_performance_npz_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        TrainMDAE(input_train_npy_path=input_train_npy_path, output_model_pth_path=output_model_pth_path, input_model_pth_path=input_model_pth_path, output_train_data_npz_path=output_train_data_npz_path, output_performance_npz_path=output_performance_npz_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def train_mdae(input_train_npy_path, output_model_pth_path, input_model_pth_path=None, output_train_data_npz_path=None, output_performance_npz_path=None, properties=None, **kwargs):

    if (output_model_pth_path is None or (os.path.exists(output_model_pth_path) and os.stat(output_model_pth_path).st_size > 0)) and \
       (output_train_data_npz_path is None or (os.path.exists(output_train_data_npz_path) and os.stat(output_train_data_npz_path).st_size > 0)) and \
       (output_performance_npz_path is None or (os.path.exists(output_performance_npz_path) and os.stat(output_performance_npz_path).st_size > 0)) and \
       True:
        print("WARN: Task TrainMDAE already executed.")
    else:
        _trainmdae( input_train_npy_path,  output_model_pth_path,  input_model_pth_path,  output_train_data_npz_path,  output_performance_npz_path,  properties, **kwargs)