from compass.testcase import run_steps, get_testcase_default
from compass.ocean.tests.global_ocean import forward
from compass.ocean.tests import global_ocean
from compass.validate import compare_timers


def collect(mesh_name):
    """
    Get a dictionary of testcase properties

    Parameters
    ----------
    mesh_name : str
        The name of the mesh

    Returns
    -------
    testcase : dict
        A dict of properties of this test case, including its steps
    """
    description = 'Global Ocean {} - Performance Test'.format(mesh_name)
    module = __name__

    name = module.split('.')[-1]
    subdir = '{}/{}'.format(mesh_name, name)
    steps = dict()

    step = forward.collect(mesh_name=mesh_name, cores=4, threads=1)
    steps[step['name']] = step

    testcase = get_testcase_default(module, description, steps, subdir=subdir)
    testcase['mesh_name'] = mesh_name

    return testcase


def configure(testcase, config):
    """
    Modify the configuration options for this testcase.

    Parameters
    ----------
    testcase : dict
        A dictionary of properties of this testcase from the ``collect()``
        function

    config : configparser.ConfigParser
        Configuration options for this testcase, a combination of the defaults
        for the machine, core and configuration
    """
    global_ocean.configure(testcase, config)


def run(testcase, test_suite, config, logger):
    """
    Run each step of the testcase

    Parameters
    ----------
    testcase : dict
        A dictionary of properties of this testcase from the ``collect()``
        function

    test_suite : dict
        A dictionary of properties of the test suite

    config : configparser.ConfigParser
        Configuration options for this testcase, a combination of the defaults
        for the machine, core and configuration

    logger : logging.Logger
        A logger for output from the testcase
    """
    steps = ['forward']
    work_dir = testcase['work_dir']
    run_steps(testcase, test_suite, config, steps, logger)
    timers = ['time integration']
    compare_timers(timers, config, work_dir, rundir1='forward')
