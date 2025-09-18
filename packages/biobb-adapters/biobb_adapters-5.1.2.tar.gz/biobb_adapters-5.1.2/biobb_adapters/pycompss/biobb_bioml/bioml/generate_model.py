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
from biobb_bioml.bioml.generate_model import model  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_excel=FILE_IN, input_hyperparameter=FILE_IN, sheets=FILE_IN, label=FILE_IN, output_model=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _model(input_excel, input_hyperparameter, sheets, label, output_model,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        model(input_excel=input_excel, input_hyperparameter=input_hyperparameter, sheets=sheets, label=label, output_model=output_model, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def generate_model(input_excel, input_hyperparameter, sheets, label, output_model, properties=None, **kwargs):

    if (output_model is None or (os.path.exists(output_model) and os.stat(output_model).st_size > 0)) and \
       True:
        print("WARN: Task model already executed.")
    else:
        _model( input_excel,  input_hyperparameter,  sheets,  label,  output_model,  properties, **kwargs)