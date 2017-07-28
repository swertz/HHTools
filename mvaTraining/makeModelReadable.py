#!/usr/bin/env python

import argparse
import h5py
import os
from shutil import copyfile

def make_readable(_in, _out):
    copyfile(_in, _out)
    f = h5py.File(_out, 'r+')
    del f['optimizer_weights']
    f.close()

if __name__ == "__main__":
    descr = """Make model file produced by keras 1.X readable in keras 2.X.
    The new file can only be used to evaluate the model, not continue training."""

    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('-i', '--input', metavar='FILE', help='Trained model H5 file', type=str, required=True)
    parser.add_argument('-o', '--output', metavar='FILE', help='Ouput readable trained model', type=str, required=True)
    args = parser.parse_args()

    make_readable(args.input, args.output)
