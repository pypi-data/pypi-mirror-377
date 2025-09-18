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
from biobb_haddock.haddock.rigid_body import RigidBody  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_haddock_wf_data_zip=FILE_IN, docking_output_zip_path=FILE_OUT, ambig_restraints_table_path=FILE_IN, unambig_restraints_table_path=FILE_IN, hb_restraints_table_path=FILE_IN, output_haddock_wf_data_zip=FILE_OUT, haddock_config_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _rigidbody(input_haddock_wf_data_zip, docking_output_zip_path, ambig_restraints_table_path, unambig_restraints_table_path, hb_restraints_table_path, output_haddock_wf_data_zip, haddock_config_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        RigidBody(input_haddock_wf_data_zip=input_haddock_wf_data_zip, docking_output_zip_path=docking_output_zip_path, ambig_restraints_table_path=ambig_restraints_table_path, unambig_restraints_table_path=unambig_restraints_table_path, hb_restraints_table_path=hb_restraints_table_path, output_haddock_wf_data_zip=output_haddock_wf_data_zip, haddock_config_path=haddock_config_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def rigid_body(input_haddock_wf_data_zip, docking_output_zip_path, ambig_restraints_table_path=None, unambig_restraints_table_path=None, hb_restraints_table_path=None, output_haddock_wf_data_zip=None, haddock_config_path=None, properties=None, **kwargs):

    if (docking_output_zip_path is None or (os.path.exists(docking_output_zip_path) and os.stat(docking_output_zip_path).st_size > 0)) and \
       (output_haddock_wf_data_zip is None or (os.path.exists(output_haddock_wf_data_zip) and os.stat(output_haddock_wf_data_zip).st_size > 0)) and \
       True:
        print("WARN: Task RigidBody already executed.")
    else:
        _rigidbody( input_haddock_wf_data_zip,  docking_output_zip_path,  ambig_restraints_table_path,  unambig_restraints_table_path,  hb_restraints_table_path,  output_haddock_wf_data_zip,  haddock_config_path,  properties, **kwargs)