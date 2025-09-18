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
from biobb_bioml.bioml.feature_selection import selection  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_features=FILE_IN, label=FILE_IN, output_excel=FILE_OUT, output_zip=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _selection(input_features, label, output_excel, output_zip,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        selection(input_features=input_features, label=label, output_excel=output_excel, output_zip=output_zip, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def feature_selection(input_features, label, output_excel, output_zip, properties=None, **kwargs):

    if (output_excel is None or (os.path.exists(output_excel) and os.stat(output_excel).st_size > 0)) and \
       (output_zip is None or (os.path.exists(output_zip) and os.stat(output_zip).st_size > 0)) and \
       True:
        print("WARN: Task selection already executed.")
    else:
        _selection( input_features,  label,  output_excel,  output_zip,  properties, **kwargs)