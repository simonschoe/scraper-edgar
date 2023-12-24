#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions for downloading corporate filings from SEC EDGAR.

Usage:
    edgar_utils.py sample-filings [--start=INT] [--end=INT] [--form-type=STR] [--section-type=STR] [-N=INT | --no-of-filings=INT] [--seed=INT]
    edgar_utils.py gather-sections [--form-type=STR] [--section-type=STR] [--min-sec-length=INT]

Options:
    -h, --help
    --start=INT                     Start year for scraping [default: 1996].
    --end=INT                       End year for scraping [default: 2020].
    --form-type=STR                 Form type [default: 10-k].
    --section-type=STR              Section type (one of: mda, item1) [default: mda].
    -N=INT, --no-of-filings=INT     Number of filings to be sampled per quarter [default: 10].
    --seed=INT                      Random seed for sampling [default: 2020].
    --min-sec-length=INT            Minimum length of section in characters [default: 2500].

"""


# standard libraries
import csv
import itertools
import shutil
import random
from pathlib import Path

# third libraries
from docopt import docopt


def sample_filings(start: int, end: int,
                   form_type: str = '10-k',
                   section_type: str = 'mda',
                   n: int = 10,
                   seed: int = 999):
    """ Create random sample for manual validation and save sample information locally
    :param int start:
        Start year for scraping
    :param int start:
        End year for scraping
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    :param str section_type:
        Section type (one of: mda, item1)
    :param int n:
        Number of filings to be sampled per quarter
    :param int seed:
        Random seed for sampling
    """
    random.seed(seed)
    path_sample = Path('output', 'sample')
    path_sample_csv = Path('output', 'sample', f'{form_type}_sample.csv')

    if not path_sample.exists():
        path_sample.mkdir()
    if not path_sample_csv.exists():
        with path_sample_csv.open('w', encoding='utf-8') as f:
            w = csv.DictWriter(f, ['id', 'year', 'quarter', 'file_name'], delimiter=';', lineterminator='\n')
            w.writeheader()

    for year, qtr in itertools.product(range(start, end + 1), range(1, 4 + 1)):
        path_filings_dir = Path('output', 'filings', form_type, str(year), f'q{qtr}')
        filings = [f.name for f in path_filings_dir.rglob('*.txt') if '_' not in f.stem]
        try:
            f_samples = random.sample(filings, n)

            with path_sample_csv.open('a', encoding='utf-8') as f:
                w = csv.DictWriter(f, ['id', 'year', 'quarter', 'file_name'], delimiter=';', lineterminator='\n')

                for s in f_samples:
                    w.writerow({'year': year, 'quarter': qtr, 'file_name': s})
                    shutil.copy(
                        Path('output', 'filings', form_type, str(year), f'q{qtr}', s),
                        Path(path_sample, s)
                    )
                    shutil.copy(
                        Path('output', 'filings', form_type, str(year), f'q{qtr}', s.replace('.txt', f'_{section_type}.txt')),
                        Path(path_sample, s.replace('.txt', f'_{section_type}.txt'))
                    )
        except Exception as e:
            print(type(e).__name__, e)
            break


def gather_sections(form_type: str = '10-k',
                    section_type: str = 'mda',
                    min_sec_length: int = 2_500):
    """ Gather all filings in one large `.txt` file as corpus with each filing delimited by a new-line
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    :param str section_type:
        Section type (one of: mda, item1)
    :param int min_sec_length:
        Minimum length of section in characters
    """

    path_filings_dir = Path('output', 'filings', form_type)
    path_filings_pooled = Path('output', 'filings', form_type, f'all_{section_type}.txt')

    for path in path_filings_dir.rglob(f'*_{section_type}.txt'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        if len(txt) > min_sec_length:
            with path_filings_pooled.open('a', encoding='utf-8', errors='ignore') as f:
                f.write(txt + '\n')


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['sample-filings']:
        sample_filings(int(args['--start']), int(args['--end']), args['--form-type'], args['--section-type'], int(args['--no-of-filings']))
    elif args['gather-sections']:
        gather_sections(args['--form-type'], args['--section-type'], int(args['--min-sec-length']))
