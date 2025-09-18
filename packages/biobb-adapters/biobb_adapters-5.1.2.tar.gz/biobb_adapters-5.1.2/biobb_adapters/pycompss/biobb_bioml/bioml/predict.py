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
from biobb_bioml.bioml.predict import Predict  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_excel=FILE_IN, input_fasta=FILE_IN, extracted=FILE_IN, prediction_results=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _predict(input_excel, input_fasta, extracted, prediction_results,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Predict(input_excel=input_excel, input_fasta=input_fasta, extracted=extracted, prediction_results=prediction_results, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def predict(input_excel, input_fasta, extracted, prediction_results, properties=None, **kwargs):

    if (prediction_results is None or (os.path.exists(prediction_results) and os.stat(prediction_results).st_size > 0)) and \
       True:
        print("WARN: Task Predict already executed.")
    else:
        _predict( input_excel,  input_fasta,  extracted,  prediction_results,  properties, **kwargs)