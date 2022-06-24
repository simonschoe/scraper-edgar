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


def sample_filings(start:int, end:int, form_type:str='10-k', section_type:str='mda', n:int=10, seed:int=999):
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
    PATH_SAMPLE = Path('output', 'sample')
    PATH_SAMPLE_CSV = Path('output', 'sample', f'{form_type}_sample.csv')
    
    if not PATH_SAMPLE.exists():
        PATH_SAMPLE.mkdir()
    if not PATH_SAMPLE_CSV.exists():
        with PATH_SAMPLE_CSV.open('w') as f:
            w = csv.DictWriter(f, ['id', 'year', 'quarter', 'file_name'], delimiter=';', lineterminator='\n')
            w.writeheader()
    
    for year, qtr in itertools.product(range(start, end+1), range(1, 4+1)):
        PATH_FILINGS_DIR = Path('output', 'filings', form_type, str(year), f'q{qtr}')
        filings = [f.name for f in PATH_FILINGS_DIR.rglob('*.txt') if '_' not in f.stem]
        try:
            f_samples = random.sample(filings, n)
            
            with PATH_SAMPLE_CSV.open('a') as f:
                w = csv.DictWriter(f, ['id', 'year', 'quarter', 'file_name'], delimiter=';', lineterminator='\n')
                
                for s in f_samples:
                    w.writerow({'year': year, 'quarter': qtr, 'file_name': s})
                    shutil.copy(
                        Path('output', 'filings', form_type, str(year), f'q{qtr}', s),
                        Path(PATH_SAMPLE, s)
                    )
                    shutil.copy(
                        Path('output', 'filings', form_type, str(year), f'q{qtr}', s.replace('.txt', f'_{section_type}.txt')),
                        Path(PATH_SAMPLE, s.replace('.txt', f'_{section_type}.txt'))
                    ) 
        except:
            break     


def gather_sections(form_type:str='10-k', section_type:str='mda', min_sec_length:int=2500):
    """ Gather all filings in one large `.txt` file as corpus with each filing delimited by a new-line
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    :param str section_type:
        Section type (one of: mda, item1)
    :param int min_sec_length:
        Minimum length of section in characters
    """ 
    
    PATH_FILINGS_DIR = Path('output', 'filings', form_type)
    PATH_FILINGS_POOLED = Path('output', 'filings', form_type, f'all_{section_type}.txt')
    
    for path in PATH_FILINGS_DIR.rglob(f'*_{section_type}.txt'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        if len(txt) > min_sec_length:
            with PATH_FILINGS_POOLED.open('a', encoding='utf-8', errors='ignore') as f:
                f.write(txt + '\n')


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['sample-filings']:
        sample_filings(int(args['--start']), int(args['--end']), args['--form-type'], args['--section-type'], int(args['--no-of-filings']))
    elif args['gather-sections']:
        gather_sections(args['--form-type'], args['--section-type'], int(args['--min-sec-length']))
