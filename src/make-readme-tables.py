#!/usr/bin/env python

"""
Make a README file with the head of each table produced
  (it must be integrated into the main README file)

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-06

"""


import pandas as pd
import os
from parse_args import parse_io


def main():
    args = parse_io()

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(args.output, 'w') as f_out:
        for f_in in args.input_list:
            dir, file = os.path.split(f_in)
            df = pd.read_table(f_in, dtype=str)
            readme_table = df \
                .head() \
                .to_markdown(
                    index=False, 
                    tablefmt='github')
            f_out.write(f'### {file.split(".")[0]}\n')
            f_out.write(readme_table)
            if file=='msa_patent_info.tsv.zip':
                frac_no_uspc = df[df.uspc_class.isna()] \
                    .patent_id.nunique()/df.patent_id.nunique()
                f_out.write((
                    '\n\nNotes:\n'
                    '* Rename *patent_id* as *forward_citation_id* '
                    'to merge this table with the *msa_citation* table.\n'
                    f'* {frac_no_uspc:.1%} '
                    'of the *patent_id*s have no *uspc_class* '
                    '(most of which, very old or very recent patents).'))
            f_out.write('\n\n\n')


if __name__ == '__main__':
    main()
