import os
import shutil
import sys

from lxml import etree

import compass
from compass.io import symlink
from compass.job import write_job_script
from compass.landice.tests.ismip6_run.ismip6_ais_proj2300_tp_branches.resample_forcing import (  # noqa
    resample_forcing,
)
from compass.model import make_graph_file, run_model
from compass.step import Step


class climateBranch(Step):
    """
    """
    def __init__(self, test_case, branch_type, branch_year):
        """
        """
        if branch_type not in ['stable', 'return']:
            sys.exit(f'"branch_type" unknown: {branch_type}')
        self.branch_type = branch_type
        self.branch_year = branch_year
        self.name = f'{branch_type}_{branch_year}'

        super().__init__(test_case=test_case, name=self.name)

    def setup(self):
        """
        """
        print(f'Setting up {self.branch_type} climate',
              f'branch year {self.branch_year}')

        config = self.config
        section = config['ismip6_ais_proj2300_tp_branches']
        base_exp_dir = section.get('base_exp_dir')

        self.ntasks = section.getint('ntasks')
        self.min_tasks = self.ntasks

        # copy over the following:
        # restart file
        rst_file = os.path.join(base_exp_dir,
                                f'rst.{self.branch_year}-01-01.nc')
        shutil.copy(rst_file,
                    os.path.join(self.work_dir,
                                 f'rst.{self.branch_year}-01-01.nc'))

        # create restart_timestamp
        with open(os.path.join(self.work_dir, 'restart_timestamp'), 'w') as f:
            f.write(f'{self.branch_year:04}-01-01_00:00:00')

        # yaml file
        shutil.copy(os.path.join(base_exp_dir, 'albany_input.yaml'),
                    self.work_dir)

        # set up namelist
        # start with the namelist from the spinup
        # Note: this differs from most compass tests, which would start with
        # the default namelist from the mpas build dir
        namelist = compass.namelist.ingest(os.path.join(base_exp_dir,
                                                        'namelist.landice'))
        options = {'config_do_restart': ".true.",
                   'config_start_time': "'file'"}
        namelist = compass.namelist.replace(namelist, options)
        compass.namelist.write(namelist, os.path.join(self.work_dir,
                                                      'namelist.landice'))

        # set up streams
        shutil.copy(os.path.join(base_exp_dir, 'streams.landice'),
                    self.work_dir)
        tree = etree.parse(os.path.join(self.work_dir, 'streams.landice'))
        root = tree.getroot()
        for child in root:
            if child.get('name') == 'ismip6_smb':
                smb_fname = child.get('filename_template')
                child.set('filename_template', 'resampled_smb.nc')
                child.set('reference_time',
                          f"{self.branch_year:04}-01-01_00:00:00")
                child.set('input_interval', "0001-00-00_00:00:00")
            if child.get('name') == 'ismip6_TF':
                tf_fname = child.get('filename_template')
                child.set('filename_template', 'resampled_tf.nc')
                child.set('reference_time',
                          f"{self.branch_year:04}-01-01_00:00:00")
                child.set('input_interval', "0001-00-00_00:00:00")
        etree.indent(tree, space="    ", level=0)
        tree.write(os.path.join(self.work_dir, 'streams.landice'))

        if self.branch_type == 'stable':
            refyear = self.branch_year
        elif self.branch_type == 'return':
            refyear = 2000
        else:
            sys.exit(f'"branch_type" unknown: {self.branch_type}')

        # create custom smb forcing file
        resample_forcing(os.path.join(base_exp_dir, smb_fname),
                         os.path.join(self.work_dir, 'resampled_smb.nc'),
                         refyear - 5,
                         refyear + 5,
                         self.branch_year, 2301)

        # create custom tf forcing file
        resample_forcing(os.path.join(base_exp_dir, tf_fname),
                         os.path.join(self.work_dir, 'resampled_tf.nc'),
                         refyear - 5,
                         refyear + 5,
                         self.branch_year, 2301)

        self.add_model_as_input()

        # set job name to run number so it will get set in batch script
        # Note: currently, for this to work right, one has to delete/comment
        # the call to write_job_script at line 316-7 in compass/setup.py
        self.config.set('job', 'job_name', self.name)
        machine = self.config.get('deploy', 'machine')
        pre_run_cmd = ('LOGDIR=previous_logs_`date +"%Y-%m-%d_%H-%M-%S"`;'
                       'mkdir $LOGDIR; cp log* $LOGDIR; date')
        post_run_cmd = "date"
        write_job_script(self.config, machine,
                         target_cores=self.ntasks, min_cores=self.min_tasks,
                         work_dir=self.work_dir,
                         pre_run_commands=pre_run_cmd,
                         post_run_commands=post_run_cmd)

        # COMPASS does not create symlinks for the load script in step dirs,
        # so use the standard approach for creating that symlink in each
        # step dir.
        if 'LOAD_COMPASS_ENV' in os.environ:
            script_filename = os.environ['LOAD_COMPASS_ENV']
            # make a symlink to the script for loading the compass conda env.
            symlink(script_filename, os.path.join(self.work_dir,
                                                  'load_compass_env.sh'))

    def run(self):
        """
        Run this member of the ensemble.
        Eventually we want this function to handle restarts.
        """

        make_graph_file(mesh_filename=f'rst.{self.branch_year}-01-01.nc',
                        graph_filename='graph.info')
        run_model(self)
