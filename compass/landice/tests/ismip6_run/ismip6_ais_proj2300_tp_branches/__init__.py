import os

import numpy as np

from compass.landice.tests.ismip6_run.ismip6_ais_proj2300_tp_branches.set_up_branches import (  # noqa
    InitialClimateBranch,
    SteadyClimateBranch,
)
from compass.testcase import TestCase


class Ismip6AisProj2300TpBranches(TestCase):
    """
    A test case for automated setup of an ensemble of branch simulations
    from an existing ISMIP6-AIS-2300 run that explore tipping points.
    """

    def __init__(self, test_group):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.landice.tests.ismip6_run.Ismip6Run
            The test group that this test case belongs to

        """
        name = 'ismip6_ais_proj2300_tp_branches'

        super().__init__(test_group=test_group, name=name,
                         subdir=name)

    def configure(self):
        """
        Set up the desired ISMIP6 AIS 2300 branch experiments.
        """
        config = self.config
        section = config['ismip6_ais_proj2300_tp_branches']

        branch_interval = section.getint('branch_interval')

        branch_points = np.arange(2000 + branch_interval, 2200,
                                  branch_interval)
        print("Setting up branch points at:", branch_points)

        # create steady climate branch runs
        for yr in branch_points:
            self.add_step(SteadyClimateBranch(test_case=self, branch_year=yr))

        # create initial climate branch runs
        # for yr in np.arange(2000, 2300, branch_interval):
        #     self.add_step(InitialClimateBranch(test_case=self, year=yr))

    def run(self):
        """
        A dummy run method
        """
        raise ValueError("ERROR: 'compass run' has no functionality at the "
                         "test case level for this test.  "
                         "Please submit the job script in "
                         "each experiment's subdirectory manually instead.")

    # no validate() method is needed
