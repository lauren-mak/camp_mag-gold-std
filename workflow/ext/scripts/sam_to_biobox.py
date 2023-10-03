import argparse
import csv
from os.path import getsize
import statistics


def main(args):
    # Relevant information in the SAM file- column 0, column 1 (length), column 5 element 0 after ‘_’ split
    # rename = False
    # if getsize(args.f_names) != 0:
    #     rename = True
    #     name_dct = dict(filter(None, csv.reader(open(args.f_names, 'r'))))
    ctgs_refs_dct = {}
    with open(args.f_in, 'r') as fi:
        for l in fi:
            info = l.split('\t')
            rname = info[5].split('_')[0] # Expected format: MGYG000000019_1 taxid_chromosome
            # if rename:
            #     rname = name_dct[rname]
            if info[0] not in ctgs_refs_dct:
                ctgs_refs_dct[info[0]] = [info[1]]
            ctgs_refs_dct[info[0]].extend(rname)

    with open(args.f_out, 'w') as fo:
        fo.write("#CAMI Format for Binning\n@Version:0.9.0\n@SampleID:_SAMPLEID_\n@@SEQUENCEID\tBINID\tLENGTH\n")
        for c,info in ctgs_refs_dct.items():
            ref = info[1] # The reference genome it maps to first
            if len(set(info[1:])) > 1:
                ref = statistics.mode(info[1:]) # The reference genome it maps to most (in terms of instances, not overall mapping region size)
            fo.write("%s\t%s\t%s\n" % (c, ref, info[0]))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("f_in", help="Contig-to-gold standard SAM")
    # parser.add_argument("f_names", help="Converts gold standard labels to a species name")
    parser.add_argument("f_out", help="Contig-to-gold standard biobox")
    args = parser.parse_args() 
    main(args)