"""
created at: 2018-05-16
author:     Volodymyr Biryuk

Module for functions that are reused throughout the project.
"""
import datetime
import gzip


def read_file(full_path: str, mode: str = 'r'):
    try:
        with open(full_path, mode) as f:
            file = f.read()
            return file
    except Exception as e:
        raise e


def write_file(full_path: str, file):
    try:
        with open(full_path, 'w') as f:
            f.write(file)
    except Exception as e:
        raise e


def unzip(full_path):
    try:
        with gzip.open(full_path, 'rb') as f:
            file_content = f.read()
            unzipped_file = file_content
    except Exception as e:
        raise e
    return unzipped_file


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    serialized = None
    if isinstance(obj, datetime.datetime):
        serialized = obj.__str__()
    return serialized
