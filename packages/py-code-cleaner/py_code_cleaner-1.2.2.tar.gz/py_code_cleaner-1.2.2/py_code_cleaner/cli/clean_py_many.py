
from typing import Optional, Sequence

import sys
import argparse

from ..py_code_cleaner import clean_py_many
from .utils import add_common_args, extract_common_kwargs

#region CLI

parser = argparse.ArgumentParser(
    prog='clean-py-many',
    description='Cleans *.py files from comments, empty lines, annotations and docstrings',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'sources', type=str, nargs='+',
    help=(
        'paths to python files or files directories to be cleaned; '
        'all results will be saved in destination directory with same relative names as in input;'
        'absolute paths will be cut to base names, recommended to use relative paths'
    )
)

parser.add_argument(
    '--destination', '-d', type=str, required=True,
    help='destination directory'
)

add_common_args(parser)


def main(args: Optional[Sequence[str]] = None):
    kwargs = parser.parse_args(args or sys.argv[1:])

    clean_py_many(
        kwargs.sources, kwargs.destination,
        **extract_common_kwargs(kwargs)
    )


#endregion


if __name__ == '__main__':
    main()