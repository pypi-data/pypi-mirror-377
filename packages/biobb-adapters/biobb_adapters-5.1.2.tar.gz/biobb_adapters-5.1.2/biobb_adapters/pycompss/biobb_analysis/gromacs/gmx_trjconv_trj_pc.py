import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_analysis.gromacs import gmx_trjconv_trj

@task(input_traj_path=FILE_IN,, output_traj_path=FILE_OUT, input_index_path=FILE_IN)
def gmx_trjconv_trj_pc(input_traj_path, output_traj_path, input_index_path, properties, **kwargs):
    try:
        gmx_trjconv_trj.GMXTrjConvTrj(input_traj_path=input_traj_path, output_traj_path=output_traj_path, input_index_path=input_index_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_traj_path)
