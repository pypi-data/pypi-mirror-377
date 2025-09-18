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
from biobb_bioml.bioml.feature_extraction import extraction  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_fasta=FILE_IN, pssm=FILE_IN, every_features=FILE_OUT, new_features=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _extraction(input_fasta, pssm, every_features, new_features,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        extraction(input_fasta=input_fasta, pssm=pssm, every_features=every_features, new_features=new_features, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def feature_extraction(input_fasta, pssm, every_features, new_features, properties=None, **kwargs):

    if (every_features is None or (os.path.exists(every_features) and os.stat(every_features).st_size > 0)) and \
       (new_features is None or (os.path.exists(new_features) and os.stat(new_features).st_size > 0)) and \
       True:
        print("WARN: Task extraction already executed.")
    else:
        _extraction( input_fasta,  pssm,  every_features,  new_features,  properties, **kwargs)