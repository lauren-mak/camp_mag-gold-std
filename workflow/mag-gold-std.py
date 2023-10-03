'''CLI for the CAMP MAG Gold-Standard Evaluation module.'''


import click
from click_default_group import DefaultGroup
from contextlib import redirect_stdout
from os import getcwd, makedirs
from os.path import abspath, dirname, exists, join
import pandas as pd
from snakemake import snakemake, main
from shutil import rmtree
from utils import Workflow_Dirs, print_cmds, cleanup_files


@click.group(cls = DefaultGroup, default = 'run', default_if_no_args = True)
def cli():
    pass


def sbatch(workflow, work_dir, samples, references, env_yamls, pyaml, cores, env_dir, s_dir):
    cfg_wd = 'work_dir=%s' % work_dir
    cfg_sp = 'samples=%s' % samples
    cfg_rf = 'references=%s' % references
    cfg_ey = 'env_yamls=%s' % env_yamls
    main([
        '--snakefile',      workflow, 
        '--config',         *{cfg_wd, cfg_sp, cfg_ey},
        '--configfiles',    *[pyaml],
        '--jobs',           str(cores),
        '--restart-times',  '2',
        '--use-conda',
        '--conda-frontend', 'conda',
        '--conda-prefix',   env_dir,
        '--printshellcmds',
        '--keep-going',
        '--latency-wait',   '60',
        '--profile',        s_dir
    ])


def cmd_line(workflow, work_dir, samples, references, env_yamls, pyaml, cores, env_dir, dry_run, unlock):
    snakemake(
        workflow,
        config = {
            'work_dir': work_dir,
            'samples': samples,
            'references': references,
            'env_yamls': env_yamls
        },
        configfiles = [
            pyaml
        ],
        cores = cores,
        restart_times = 2,
        use_conda = True,
        conda_prefix = env_dir,
        printshellcmds = True,
        keepgoing = True,
        latency_wait = 60,
        dryrun = dry_run,
        unlock = unlock
    )


@cli.command('run')
@click.option('-c', '--cores', type = int, default = 1, show_default = True, \
    help = 'In local mode, the number of CPU cores available to run rules. \n\
    In Slurm mode, the number of sbatch jobs submitted in parallel. ')
@click.option('-d', '--work_dir', type = click.Path(), required = True, \
    help = 'Absolute path to working directory')
@click.option('-s', '--samples', type = click.Path(), required = True, \
    help = 'Sample CSV in format [sample_name,...,]')
@click.option('-r', '--references', type = click.Path(), required = True, \
    help = 'Reference CSV in format [sample_name,...,]')
@click.option('-p', '--parameters', type = click.Path(), required = False, \
    help = 'Absolute path to parameters and resources YAML file')
# @click.option('--unit_test', is_flag = True, default = False, \
#     help = 'Generate unit tests using the Snakemake API')
@click.option('--slurm', is_flag = True, default = False, \
    help = 'Run workflow by submitting rules as Slurm cluster jobs')
@click.option('--dry_run', is_flag = True, default = False, \
    help = 'Set up directory structure and print workflow commands to be run separately')
@click.option('--unlock', is_flag = True, default = False, \
    help = 'Remove a lock on the work directory')
@click.option('--version', is_flag = True, default = False, \
    help = 'Check the module version')
def run(cores, work_dir, samples, references, parameters, slurm, dry_run, unlock, version): # unit_test
    # Get the absolute path of the Snakefile to find the profile configs
    main_dir = dirname(dirname(abspath(__file__))) # /path/to/main_dir/workflow/cli.py
    workflow = join(main_dir, 'workflow', 'Snakefile')

    if version:
        f = open(join(main_dir, 'workflow', '__init__.py')).readlines()
        m = f[0].replace('"""Top-level package for the ', '').replace(' module."""', '')
        v = f[4].split(' = ')[1]
        print('{}: version {}'.format(m, v))
        return

    # Set location of rule (and program) parameters and resources
    pyaml = parameters if parameters else join(main_dir, 'configs', 'config.yaml')

    # Set up the conda environment directory
    env_dir = join(main_dir, 'conda_envs')
    if not exists(env_dir):
        makedirs(env_dir)
    env_yamls = join(main_dir, 'configs', 'conda')

    # If generating unit tests, set the unit test directory (by default, is pytest's default, .tests)
    # unit_test_dir = join(main_dir, '.tests/unit') if unit_test else None

    # If rules failed previously, unlock the directory
    if unlock:
        cmd_line(workflow, work_dir, samples, references, env_yamls, pyaml,   \
                 cores, env_dir, False, unlock)
        rmtree(join(getcwd(), '.snakemake'))
        
    # Run workflow
    if slurm:
        sbatch(workflow, work_dir, samples, references, env_yamls, pyaml,     \
               cores, env_dir, join(main_dir, 'configs', 'sbatch'))
    elif dry_run:
        # Set up the directory structure skeleton
        Workflow_Dirs(work_dir, 'mag-gold-std')
        # Print the dry run standard out
        f = io.StringIO()
        with redirect_stdout(f):
            cmd_line(workflow, work_dir, samples, references, env_yamls, pyaml,   \
                     cores, env_dir, True, False)
        print_cmds(f.getvalue())
    else:
        cmd_line(workflow, work_dir, samples, references, env_yamls, pyaml,   \
                 cores, env_dir, False, False)


@cli.command('cleanup')
@click.option('-d', '--work_dir', type = click.Path(), required = True, \
    help = 'Absolute path to working directory')
@click.option('-s', '--samples', type = click.Path(), required = True, \
    help = 'Sample CSV in format [sample_name,...,]')
def cleanup(work_dir, samples): 
    df = pd.read_csv(samples, header = 0, index_col = 0) # name, fwd, rev
    cleanup_files(work_dir, df)


@cli.command('test')
def test(): 
    main_dir = dirname(dirname(abspath(__file__))) # /path/to/main_dir/workflow/cli.py
    workflow = join(main_dir, 'workflow', 'Snakefile')
    work_dir = join(main_dir, 'test_out')
    samples = join(main_dir, 'test_data', 'samples.csv')
    references = join(main_dir, 'test_data', 'references.csv')
    
    # Set location of rule (and program) parameters and resources
    pyaml = join(main_dir, 'test_data', 'config.yaml')

    # Set up the conda environment directory
    env_dir = join(main_dir, 'conda_envs')
    if not exists(env_dir):
        makedirs(env_dir)
    env_yamls = join(main_dir, 'configs', 'conda')
    
    # Run workflow
    cmd_line(workflow, work_dir, samples, references, env_yamls, pyaml,   \
             10, env_dir, False, False)


cli.add_command(run)
cli.add_command(cleanup)
cli.add_command(test)


if __name__ == '__main__':
    cli()
