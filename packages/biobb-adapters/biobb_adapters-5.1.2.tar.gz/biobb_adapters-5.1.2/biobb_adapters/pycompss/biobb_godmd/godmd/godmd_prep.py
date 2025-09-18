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
from biobb_godmd.godmd.godmd_prep import GOdMDPrep  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_orig_path=FILE_IN, input_pdb_target_path=FILE_IN, output_aln_orig_path=FILE_OUT, output_aln_target_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _godmdprep(input_pdb_orig_path, input_pdb_target_path, output_aln_orig_path, output_aln_target_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GOdMDPrep(input_pdb_orig_path=input_pdb_orig_path, input_pdb_target_path=input_pdb_target_path, output_aln_orig_path=output_aln_orig_path, output_aln_target_path=output_aln_target_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def godmd_prep(input_pdb_orig_path, input_pdb_target_path, output_aln_orig_path, output_aln_target_path, properties=None, **kwargs):

    if (output_aln_orig_path is None or (os.path.exists(output_aln_orig_path) and os.stat(output_aln_orig_path).st_size > 0)) and \
       (output_aln_target_path is None or (os.path.exists(output_aln_target_path) and os.stat(output_aln_target_path).st_size > 0)) and \
       True:
        print("WARN: Task GOdMDPrep already executed.")
    else:
        _godmdprep( input_pdb_orig_path,  input_pdb_target_path,  output_aln_orig_path,  output_aln_target_path,  properties, **kwargs)