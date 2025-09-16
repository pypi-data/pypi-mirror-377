
from typing import Dict, Any

import argparse


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        '--keep-nonpy', '-k',
        nargs="+",
        type=str, default='',
        help='additional file extensions to transfer between src and dst directories (to not ignore)'
    )

    parser.add_argument(
        '--keep-empty-lines', '-e',
        action='store_true',
        help='Whether to not remove empty lines'
    )

    parser.add_argument(
        '--keep-docstrings', '-s',
        action='store_true',
        help='Whether to not remove docstrings'
    )

    parser.add_argument(
        '--keep-annotations', '-a',
        action='store_true',
        help='Whether to not remove annotations'
    )


    parser.add_argument(
        '--skip-errors', '-i',
        action='store_true',
        help='Do not fail on problem files'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Do not print processing info'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Whether to run without performing file processing operations'
    )


def extract_common_kwargs(kwargs) -> Dict[str, Any]:
    return dict(
        keep_nonpy=kwargs.keep_nonpy.split(),
        filter_docstrings=not kwargs.keep_docstrings,
        filter_annotations=not kwargs.keep_annotations,
        filter_empty_lines=not kwargs.keep_empty_lines,
        skip_errors=kwargs.skip_errors,
        quiet=kwargs.quiet,
        dry_run=kwargs.dry_run
    )

