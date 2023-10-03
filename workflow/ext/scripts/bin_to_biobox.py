#!/usr/bin/env python

# Copyright 2020 Department of Computational Biology for Infection Research - Helmholtz Centre for Infection Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import glob


def read_fasta_file(fasta_file):
    with open(fasta_file, 'r') as read_handler:
        sequence_id = ""
        for line in read_handler:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if len(sequence_id) > 0:
                    yield sequence_id, fasta_file
                sequence_id = line[1:]
                continue
        if len(sequence_id) > 0:
            yield sequence_id, fasta_file


def convert(bin_dir, f_out):
    with open(f_out, 'w') as write_handler:
        write_handler.write("#CAMI Format for Binning\n@Version:0.9.0\n@SampleID:_SAMPLEID_\n@@SEQUENCEID\tBINID\n")
        for f in glob.glob(bin_dir + '/*.fa'):
            for sequence_id, bin_id in read_fasta_file(f):
                write_handler.write("%s\t%s\n" % (sequence_id, bin_id))


def main():
    parser = argparse.ArgumentParser(description="Convert bins in FASTA files to CAMI tsv format")
    parser.add_argument("bin_dir", help="FASTA files including full paths")
    parser.add_argument("f_out", help="Output file")
    args = parser.parse_args()
    convert(args.bin_dir, args.f_out)


if __name__ == "__main__":
    main()