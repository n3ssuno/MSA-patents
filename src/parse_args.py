#!/usr/bin/env python

"""
Modules to parse the arguments in the Makefile.

Author: Carlo Bottai
Copyright (c) 2020 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-05

"""


import argparse


def parse_io():
    parser = argparse.ArgumentParser('Names Fixer')
    parser.add_argument(
        '-i', '--input', 
        help='input file', 
        required=False)
    parser.add_argument(
        '-I', '--input_list', 
        help='list of input files', 
        required=False, 
        nargs='+')
    parser.add_argument(
        '-o', '--output', 
        help='output directory', 
        required=False)
    return parser.parse_args()
