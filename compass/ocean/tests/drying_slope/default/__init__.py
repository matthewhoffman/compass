from compass.ocean.tests.drying_slope.forward import Forward
from compass.ocean.tests.drying_slope.initial_state import InitialState
from compass.ocean.tests.drying_slope.viz import Viz
from compass.testcase import TestCase
from compass.validate import compare_variables


class Default(TestCase):
    """
    The default drying_slope test case

    Attributes
    ----------
    resolution : float
        The resolution of the test case in km

    coord_type : str
        The type of vertical coordinate (``sigma``, ``single_layer``, etc.)
    """

    def __init__(self, test_group, resolution, coord_type, method):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.drying_slope.DryingSlope
            The test group that this test case belongs to

        resolution : float
            The resolution of the test case in km

        coord_type : str
            The type of vertical coordinate (``sigma``, ``single_layer``)
        """
        name = 'default'

        self.resolution = resolution
        self.coord_type = coord_type
        if resolution < 1.:
            res_name = f'{int(resolution*1e3)}m'
        else:
            res_name = f'{int(resolution)}km'
        subdir = f'{coord_type}/{method}/{res_name}/{name}'
        super().__init__(test_group=test_group, name=name,
                         subdir=subdir)
        self.add_step(InitialState(test_case=self, resolution=resolution,
                                   coord_type=coord_type))
        damping_coeffs = None
        if coord_type == 'single_layer':
            forward_step = Forward(test_case=self, resolution=resolution,
                                   ntasks=4, openmp_threads=1,
                                   coord_type=coord_type)
            if method == 'ramp':
                forward_step.add_namelist_options(
                    {'config_zero_drying_velocity_ramp': ".true."})
            self.add_step(forward_step)
        else:
            damping_coeffs = [0.0025, 0.01]
            for damping_coeff in damping_coeffs:
                forward_step = Forward(test_case=self, resolution=resolution,
                                       name=f'forward_{damping_coeff}',
                                       ntasks=4, openmp_threads=1,
                                       damping_coeff=damping_coeff,
                                       coord_type=coord_type)
                if method == 'ramp':
                    forward_step.add_namelist_options(
                        {'config_zero_drying_velocity_ramp': ".true."})
                self.add_step(forward_step)
        self.damping_coeffs = damping_coeffs
        self.add_step(Viz(test_case=self, damping_coeffs=damping_coeffs))

    def validate(self):
        """
        Validate variables against a baseline
        """
        damping_coeffs = self.damping_coeffs
        variables = ['layerThickness', 'normalVelocity']
        if damping_coeffs is not None:
            for damping_coeff in damping_coeffs:
                compare_variables(test_case=self, variables=variables,
                                  filename1=f'forward_{damping_coeff}/'
                                            'output.nc')
        else:
            compare_variables(test_case=self, variables=variables,
                              filename1='forward/output.nc')
