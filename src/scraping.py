#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions for downloading corporate filings from SEC EDGAR.

Usage:
    edgar_scrape.py download-index [--user-agent=STR] [--start=INT] [--end=INT]
    edgar_scrape.py count-filings [--start=INT] [--end=INT] [--form-type=STR]
    edgar_scrape.py download-filings [--user-agent=STR] [--start=INT] [--end=INT] [--form-type=STR] [-N=INT | --no-of-filings=INT]
    
Options:
    -h, --help
    --user-agent=STR                Agent to identify with SEC EDGAR (of the form 'ORG_NAME MAIL_ADDRESS')
    --start=INT                     Start year for scraping [default: 1996].
    --end=INT                       End year for scraping [default: 2020].
    --form-type=STR                 Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a) [default: 10-k].
    -N INT, --no-of-filings=INT     Number of filings to be sampled per quarter [default: 10].
    
"""


# standard libraries
import csv
import itertools
import time
import datetime as dt
from pathlib import Path
from urllib.request import build_opener, install_opener, urlretrieve, urlopen

# third libraries
import pandas as pd
from docopt import docopt

# own modules
from parsing_patterns import *



def download_index(user_agent:str, start:int, end:int):
    """ Download index files from SEC EDGAR
    :param str user_agent:
        Agent to identify with SEC EDGAR (of the form 'ORG_NAME MAIL_ADDRESS')
    :param int start:
        Start year for scraping
    :param int start:
        End year for scraping
    """
    
    EDGAR_URL_INDEX = 'https://www.sec.gov/Archives/edgar/full-index'
    PATH_IND_DIR = Path('output', 'index')
    if not PATH_IND_DIR.exists():
        PATH_IND_DIR.mkdir()
    
    opener = build_opener()
    opener.addheaders = [('User-Agent', user_agent)]
    install_opener(opener)
    
    for year, qtr in itertools.product(range(start, end+1), range(1, 4+1)):
        try:
            URL = f'{EDGAR_URL_INDEX}/{year}/QTR{qtr}/master.idx'
            PATH_IND = Path(PATH_IND_DIR, f'{year}_q{qtr}.idx')
            if PATH_IND.exists():
                print(f'Index file year_{year}_Q{qtr} exists already!')
            else:
                time.sleep(2)
                urlretrieve(URL, PATH_IND)
                print(f'Index file year_{year}_Q{qtr} written to {PATH_IND}')  
        except:
            print(f'Download failed! Index file for year_{year}_Q{qtr} not available via EDGAR...')
  
    
def get_form_pattern(form_type:str):
    """ Get regex pattern for specified form type to search in index file
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    :return re.Pattern:
        Regex pattern for matching form types
    """
    if form_type =='10-k':
        return PAT_10K
    elif form_type =='10-k/a':
        return PAT_10KA
    elif form_type =='10-q':
        return PAT_10Q
    elif form_type =='10-q/a':
        return PAT_10QA  
    elif form_type =='8-k':
        return PAT_8K
    else:
        print('Form not implemented! Choose one of 8-k, 10-k, 10-k/a, 10-q, 10-q/a.')
        return False
    
    
def count_filings(start:int, end:int, form_type:str='10-k'):
    """ Count number of filings per quarter and write to local CSV file
    :param int start:
        Start year for scraping
    :param int start:
        End year for scraping
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    """
    PATH_IND_DIR = Path('output', 'index')
    PATH_COUNTS = Path('output', f'counts_{form_type}.csv')
      
    if not get_form_pattern(form_type):
        return
    else:
      form_pattern = get_form_pattern(form_type)
      
    counts = []
    for year, qtr in itertools.product(range(start, end+1), range(1, 4+1)):
        PATH_IND = Path(PATH_IND_DIR, f'{year}_q{qtr}.idx')
        try:
            with PATH_IND.open('r') as f:
                ctr = 1
                for line in f:
                    form_ind = form_pattern.search(line)
                    if form_ind:
                        ctr += 1
            counts.append([year, qtr, ctr])
        except:
            print(f'Error: Download index file for {year}_q{qtr} first!')
            break      

    pd.DataFrame(counts, columns=['year', 'quarter', 'no_of_filings']).to_csv(PATH_COUNTS, sep=';') 
     

def download_filings(user_agent:str, start:int, end:int, form_type:str='10-k', n:int=10):
    """ Download filings from SEC EDGAR
    :param str user_agent:
        Agent to identify with SEC EDGAR (of the form 'ORG_NAME MAIL_ADDRESS')
    :param int start:
        Start year for scraping
    :param int start:
        End year for scraping
    :param str form_type:
        Form type (one of: 8-k, 10-k, 10-k/a, 10-q, 10-q/a)
    :param int n:
        Number of filings to be downloaded per quarter
    """
    
    EDGAR_URL = 'https://www.sec.gov/Archives/'
    PATH_LOG = Path('output', 'filings', form_type, f'log_download.txt')
    PATH_META = Path('output', 'filings', form_type, 'metadata.csv')
    
    opener = build_opener()
    opener.addheaders = [('User-Agent', user_agent)] # 'WWU s_scho53@uni-muenster.de'
    install_opener(opener)
    
    if not get_form_pattern(form_type):
        return
    
    if not PATH_META.exists():
        with PATH_META.open('w') as f:
            w = csv.DictWriter(f, PAT_META.keys(), delimiter=';', lineterminator='\n')
            w.writeheader()
        
    for year, qtr in itertools.product(range(start, end+1), range(1, 4+1)):
        PATH_FILINGS_DIR = Path('output', 'filings', form_type, str(year), f'q{str(qtr)}')
        if not PATH_FILINGS_DIR.exists():
            PATH_FILINGS_DIR.mkdir(parents=True)
        try:
            with Path('output', 'index', f'{year}_q{qtr}.idx').open('r') as f:
                ctr = 1
                for line in f:
                    if ctr <= n:
                        form_ind = get_form_pattern(form_type).search(line)
                        if form_ind:
                            file_ind = PAT_FNAME.search(line)
                            if file_ind:
                                URL = f'{EDGAR_URL}/{file_ind.group(1)}'
                                PATH_FILE = Path(PATH_FILINGS_DIR, str(file_ind.group(2)))
                                if PATH_FILE.exists():
                                    log = f'Already downloaded from: {URL}\nWas written to {PATH_FILE}'
                                    ctr += 1
                                else:   
                                    log = f'Download from:\t{URL}\nWriting to:\t{PATH_FILE}'                        
                                    i = 0
                                    while True:                                    
                                        try:
                                            txt = urlopen(URL, timeout=20).read().decode('utf-8', errors='ignore')
                                            PATH_FILE.open('w', encoding='utf-8').write(txt)
                                            
                                            meta = {}
                                            for k in PAT_META.keys():
                                                meta[k] = None
                                            with PATH_FILE.open('r', encoding='utf-8') as f:
                                                for line in f:
                                                    for k, v in PAT_META.items():
                                                        meta_match = v.search(line)
                                                        if meta_match and meta[k] == None and k != 'hlink':
                                                            meta[k] = meta_match.group(1)
                                                    if PAT_HEADER_END.search(line):
                                                        break
                                                if meta['fname'] != None:
                                                    f_match = PAT_META['hlink'].search(meta['fname'])
                                                    if f_match:
                                                        meta['hlink'] = f"{EDGAR_URL}/{meta['cik']}/{f_match.group(3)}/{f_match.group(5)}/{f_match.group(6)}/{f_match.group(2)}-index.htm"
                                                with PATH_META.open('a') as f:
                                                    w = csv.DictWriter(f, PAT_META.keys(), delimiter=';', lineterminator='\n')
                                                    w.writerow(meta)
                                            
                                        except Exception as err:
                                            PATH_LOG.open('a').write(f'\n[{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {err}\n'
                                                                     f'Restart!\n') 
                                            print(f'{err}: {URL}\n'
                                                  f'Restart\n')
                                            time.sleep(5)
                                            i += 1
                                            if i < 10:
                                                continue
                                        break            
                                    ctr += 1
                                print(log, '\n')
                                PATH_LOG.open('a').write(f'\n[{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {log}\n')
        except:
            print(f'Error: Download index file for {year}_q{qtr} first!')
            break


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['download-index']:
        download_index(args['--user-agent'], int(args['--start']), int(args['--end']))
    elif args['count-filings']:
        count_filings(int(args['--start']), int(args['--end']), args['--form-type'])
    elif args['download-filings']:
        download_filings(args['--user-agent'], int(args['--start']), int(args['--end']), args['--form-type'], int(args['--no-of-filings']))