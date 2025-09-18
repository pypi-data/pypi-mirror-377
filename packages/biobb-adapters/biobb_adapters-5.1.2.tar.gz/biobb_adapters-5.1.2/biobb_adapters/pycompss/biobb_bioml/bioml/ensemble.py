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
from biobb_bioml.bioml.ensemble import Ensemble  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_excel=FILE_IN, input_hyperparameter=FILE_IN, sheets=FILE_IN, label=FILE_IN, ensemble_output=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _ensemble(input_excel, input_hyperparameter, sheets, label, ensemble_output,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Ensemble(input_excel=input_excel, input_hyperparameter=input_hyperparameter, sheets=sheets, label=label, ensemble_output=ensemble_output, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def ensemble(input_excel, input_hyperparameter, sheets, label, ensemble_output, properties=None, **kwargs):

    if (ensemble_output is None or (os.path.exists(ensemble_output) and os.stat(ensemble_output).st_size > 0)) and \
       True:
        print("WARN: Task Ensemble already executed.")
    else:
        _ensemble( input_excel,  input_hyperparameter,  sheets,  label,  ensemble_output,  properties, **kwargs)