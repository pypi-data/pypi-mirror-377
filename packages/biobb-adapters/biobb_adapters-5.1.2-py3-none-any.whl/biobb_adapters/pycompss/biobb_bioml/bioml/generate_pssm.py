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
from biobb_bioml.bioml.generate_pssm import pssm  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_fasta=FILE_IN, output_pssm=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pssm(input_fasta, output_pssm,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        pssm(input_fasta=input_fasta, output_pssm=output_pssm, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def generate_pssm(input_fasta, output_pssm, properties=None, **kwargs):

    if (output_pssm is None or (os.path.exists(output_pssm) and os.stat(output_pssm).st_size > 0)) and \
       True:
        print("WARN: Task pssm already executed.")
    else:
        _pssm( input_fasta,  output_pssm,  properties, **kwargs)