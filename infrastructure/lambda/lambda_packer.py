import argparse
import hashlib
import os
import sys
from tempfile import TemporaryDirectory


def cleanup_files(tmp_dir):
    os.system(f'find {tmp_dir} -path "*/__pycache__*" -delete 1>/dev/null')


def install_requirements(requirements, destination):
    if not requirements:
        return
    os.system(f'pip install -q -r {requirements} --target {destination} 1>/dev/null')


def copy_inputs(inputs, destination):
    for input in inputs:
        os.system(f'cp --parents -r -p {input} {destination} 1>/dev/null')


def build_zip(output_filename, requirements, inputs):
    with TemporaryDirectory() as tmp_dir:
        install_requirements(requirements, tmp_dir)
        copy_inputs(inputs, tmp_dir)
        cleanup_files(tmp_dir)
        os.system(f'mkdir -p $(dirname {output_filename})')
        os.system(f'cd {tmp_dir}; zip -X -q {output_filename} -r . >/dev/null')


def parse_args(input_args):
    parser = argparse.ArgumentParser(description='Create lambda function package')
    parser.add_argument('-r', '--requirements', dest='requirements', default=None,
                        help='the path to the pip requirements file')
    parser.add_argument('output', help='the filename of the output zip file')
    parser.add_argument('inputs', type=str, nargs='+', help='the source files to be included')
    return parser.parse_args(input_args)


if __name__ == '__main__':
    ARGS = parse_args(sys.argv[1:])
    build_zip(ARGS.output, ARGS.requirements, ARGS.inputs)
    md5sum = hashlib.md5(open(ARGS.output, 'rb').read()).hexdigest()
    result = '{"md5sum": "' + md5sum + '"}'
    print(result)
