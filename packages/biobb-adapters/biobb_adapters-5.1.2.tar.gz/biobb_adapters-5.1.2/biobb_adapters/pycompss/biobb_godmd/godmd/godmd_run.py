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
from biobb_godmd.godmd.godmd_run import GOdMDRun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_orig_path=FILE_IN, input_pdb_target_path=FILE_IN, input_aln_orig_path=FILE_IN, input_aln_target_path=FILE_IN, output_log_path=FILE_OUT, output_ene_path=FILE_OUT, output_trj_path=FILE_OUT, output_pdb_path=FILE_OUT, input_config_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _godmdrun(input_pdb_orig_path, input_pdb_target_path, input_aln_orig_path, input_aln_target_path, output_log_path, output_ene_path, output_trj_path, output_pdb_path, input_config_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GOdMDRun(input_pdb_orig_path=input_pdb_orig_path, input_pdb_target_path=input_pdb_target_path, input_aln_orig_path=input_aln_orig_path, input_aln_target_path=input_aln_target_path, output_log_path=output_log_path, output_ene_path=output_ene_path, output_trj_path=output_trj_path, output_pdb_path=output_pdb_path, input_config_path=input_config_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def godmd_run(input_pdb_orig_path, input_pdb_target_path, input_aln_orig_path, input_aln_target_path, output_log_path, output_ene_path, output_trj_path, output_pdb_path, input_config_path=None, properties=None, **kwargs):

    if (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_ene_path is None or (os.path.exists(output_ene_path) and os.stat(output_ene_path).st_size > 0)) and \
       (output_trj_path is None or (os.path.exists(output_trj_path) and os.stat(output_trj_path).st_size > 0)) and \
       (output_pdb_path is None or (os.path.exists(output_pdb_path) and os.stat(output_pdb_path).st_size > 0)) and \
       True:
        print("WARN: Task GOdMDRun already executed.")
    else:
        _godmdrun( input_pdb_orig_path,  input_pdb_target_path,  input_aln_orig_path,  input_aln_target_path,  output_log_path,  output_ene_path,  output_trj_path,  output_pdb_path,  input_config_path,  properties, **kwargs)