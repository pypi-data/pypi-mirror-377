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
from biobb_pytorch.mdae.apply_mdae import ApplyMDAE  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_data_npy_path=FILE_IN, input_model_pth_path=FILE_IN, output_reconstructed_data_npy_path=FILE_OUT, output_latent_space_npy_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _applymdae(input_data_npy_path, input_model_pth_path, output_reconstructed_data_npy_path, output_latent_space_npy_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ApplyMDAE(input_data_npy_path=input_data_npy_path, input_model_pth_path=input_model_pth_path, output_reconstructed_data_npy_path=output_reconstructed_data_npy_path, output_latent_space_npy_path=output_latent_space_npy_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def apply_mdae(input_data_npy_path, input_model_pth_path, output_reconstructed_data_npy_path, output_latent_space_npy_path=None, properties=None, **kwargs):

    if (output_reconstructed_data_npy_path is None or (os.path.exists(output_reconstructed_data_npy_path) and os.stat(output_reconstructed_data_npy_path).st_size > 0)) and \
       (output_latent_space_npy_path is None or (os.path.exists(output_latent_space_npy_path) and os.stat(output_latent_space_npy_path).st_size > 0)) and \
       True:
        print("WARN: Task ApplyMDAE already executed.")
    else:
        _applymdae( input_data_npy_path,  input_model_pth_path,  output_reconstructed_data_npy_path,  output_latent_space_npy_path,  properties, **kwargs)