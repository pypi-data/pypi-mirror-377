
from typing import Optional, Sequence

import sys
import argparse

from ..py_code_cleaner import clean_py_main
from .utils import add_common_args, extract_common_kwargs

#region CLI

parser = argparse.ArgumentParser(
    prog='clean-py',
    description='Cleans *.py files from comments, empty lines, annotations and docstrings',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('source', type=str, help='python file path or path to directory with files')

parser.add_argument(
    '--destination', '-d', type=str, default=None,
    help='destination file or directory; empty means to print to stdout'
)

add_common_args(parser)


def main(args: Optional[Sequence[str]] = None):
    kwargs = parser.parse_args(args or sys.argv[1:])

    clean_py_main(
        kwargs.source, kwargs.destination,
        **extract_common_kwargs(kwargs)
    )


#endregion


if __name__ == '__main__':
    main()



