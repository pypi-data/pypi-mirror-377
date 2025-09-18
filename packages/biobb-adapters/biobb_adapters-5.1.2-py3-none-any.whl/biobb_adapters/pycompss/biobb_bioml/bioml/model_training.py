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
from biobb_bioml.bioml.model_training import training  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_excel=FILE_IN, label=FILE_IN, hyperparameters=FILE_OUT, training_output=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _training(input_excel, label, hyperparameters, training_output,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        training(input_excel=input_excel, label=label, hyperparameters=hyperparameters, training_output=training_output, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def model_training(input_excel, label, hyperparameters, training_output, properties=None, **kwargs):

    if (hyperparameters is None or (os.path.exists(hyperparameters) and os.stat(hyperparameters).st_size > 0)) and \
       (training_output is None or (os.path.exists(training_output) and os.stat(training_output).st_size > 0)) and \
       True:
        print("WARN: Task training already executed.")
    else:
        _training( input_excel,  label,  hyperparameters,  training_output,  properties, **kwargs)