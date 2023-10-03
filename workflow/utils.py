'''Utilities.'''


# --- Workflow setup --- #


import glob
import gzip
import os
from os import makedirs, symlink
from os.path import abspath, basename, exists, join
import pandas as pd
import shutil


def extract_from_gzip(ap, out):
    if open(ap, 'rb').read(2) == b'\x1f\x8b': # If the input is gzipped
        with gzip.open(ap, 'rb') as f_in, open(out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    else: # Otherwise, symlink
        symlink(ap, out)


def ingest_samples(samples, tmp):
    df = pd.read_csv(samples, header = 0, index_col = 0) # name, mag_dir_0, mag_dir_1,...
    s = [i for i in list(df.index) if 'illumina' not in i]
    b = list(df.columns)
    lst = df.values.tolist()
    for i,l in enumerate(lst):
        if not exists(join(tmp, s[i])): # Make a temporary directory for all of the MAGs in the sample
            makedirs(join(tmp, s[i]))
            for j,m in enumerate(b):
                if not exists(join(tmp, s[i], m)): # Make a temporary directory for all of the MAGs in the sample
                    makedirs(join(tmp, s[i], m))
                    for f in glob.glob(l[j] + '/*.fa'):
                        if 'unbinned' not in f:
                            prefix = basename(f).split('.')[1]
                            symlink(abspath(f), join(tmp, s[i], m, prefix + '.fa'))
    return s


def ingest_references(references, tmp):
    df = pd.read_csv(references, header = 0, index_col = 0) # name, asm_fa, ref_dir
    s = list(df.index)
    lst = df.values.tolist()
    s2a = {}
    s2r = {}
    for i,l in enumerate(lst):
        s2a[s[i]] = l[0]
        if not exists(join(tmp, join(tmp, s[i], 'assembly.fa'))):
            symlink(abspath(l[0]), join(tmp, s[i], 'assembly.fa'))
        ref_prefix = basename(l[1])
        s2r[s[i]] = ref_prefix
        if not exists(join(tmp, ref_prefix)): # Make a temporary directory for the reference genomes
            makedirs(join(tmp, ref_prefix))
            for j,f in enumerate(glob.glob(l[1] + '/*.fa') + glob.glob(l[1] + '/*.fna') + glob.glob(l[1] + '/*.fasta')):
                symlink(abspath(f), join(tmp, ref_prefix, str(j) + '.fa'))
    return s2a,s2r


def check_make(d):
    if not exists(d):
        makedirs(d)


class Workflow_Dirs:
    '''Management of the working directory tree.'''
    OUT = ''
    TMP = ''
    LOG = ''

    def __init__(self, work_dir, module):
        self.OUT = join(work_dir, module)
        self.TMP = join(work_dir, 'tmp') 
        self.LOG = join(work_dir, 'logs') 
        check_make(self.OUT)
        out_dirs = ['0_asm_ref', '1_binners', '2_amber', 'final_reports']
        for d in out_dirs: 
            check_make(join(self.OUT, d))
        # Add a subdirectory for symlinked-in input files
        check_make(self.TMP)
        # Add custom subdirectories to organize rule logs
        check_make(self.LOG)
        log_dirs = ['mapping']
        for d in log_dirs: 
            check_make(join(self.LOG, d))


def cleanup_files(work_dir, df):
    smps = list(df.index)
    for s in smps: 
        pass


def print_cmds(f):
    # fo = basename(log).split('.')[0] + '.cmds'
    # lines = open(log, 'r').read().split('\n')
    fi = [l for l in f.split('\n') if l != '']
    write = False
    with open('commands.sh', 'w') as f_out:
        for l in fi:
            if 'rule' in l:
                f_out.write('# ' + l.strip().replace('rule ', '').replace(':', '') + '\n')
                write = False
            if 'wildcards' in l:
                f_out.write('# ' + l.strip().replace('wildcards: ', '') + '\n')
            if 'resources' in l:
                write = True
                l = ''
            if write:
                f_out.write(l.strip() + '\n')
            if 'rule make_config' in l:
                break


# --- Workflow functions --- #

