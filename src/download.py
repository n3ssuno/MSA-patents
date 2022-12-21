#!/usr/bin/env python

"""
Download needed raw data

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-05

"""


import os
import time
import random
import requests
import tempfile
import sys
import zipfile
import shutil
import tarfile
from tqdm import tqdm
from parse_args import parse_io


def download_url(url, output_dir, file_name):
    response = None
    try:
        response = requests.get(url, stream=True)
    except:
        print(f'Connection error occurred trying to get URL: {url}', 
            file=sys.stderr)
    if response is None or response.status_code != 200:
        print(f'Error {response.status_code}',
            f'while downloading file from URL: {url}')
        return None

    tmp_fd, tmp_fn = tempfile.mkstemp()
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    with os.fdopen(tmp_fd, 'wb') as f_out, \
         tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True) as progress_bar:
        if total_size_in_bytes is None:
            f_out.write(response.content)
        else:
            total_size_in_bytes = int(total_size_in_bytes)
            block_size = 1024 # 1 KB
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f_out.write(data)
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print(f'ERROR, something went wrong while downloading {url}')
    
    target = os.path.join(output_dir, file_name)
    if target.endswith('.zip') and not zipfile.is_zipfile(tmp_fn):
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as f_zip:
            f_zip.write(tmp_fn)
        os.unlink(tmp_fn)
    elif any([el.endswith('.tar') for el in url.split('?')]):
        shutil.move(tmp_fn, target)
        with tarfile.open(target) as f_tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(f_tar, output_dir)
        os.remove(target)
    else:
        shutil.move(tmp_fn, target)
    return target


def main():
    args = parse_io()
    
    source_url = args.input
    output_file = args.output
    output_dir, file_name = os.path.split(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    download_url(source_url, output_dir, file_name)
    time.sleep(random.random()*5)


if __name__ == '__main__':
    main()
