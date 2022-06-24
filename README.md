# EDGAR Scraper and MD&A/Item1 Extraction

Command-line interface (CLI) program for downloading 10-K, 10-K/A, 10-Q, 10-Q/A filings from the [SEC EDGAR database](https://www.sec.gov/edgar/about). Note that the program is not optimized for efficiency (e.g., parallelization).


### Scraping Commands

1. Setup Python environment (*version 3.8.5*)
```sh
pip install -r requirements.txt
```

2. Download index files from SEC EDGAR for the period `--start` to `--end` (write to `output/index`).
```sh
python src/scraping.py download-index --user-agent 'ORG_NAME MAIL_ADDRESS' --start 2000 --end 2004
```

3. Compute number of available filings (write to `output`).
```sh
python src/scraping.py count-filings --start 1996 --end 2022 --form-type 10-k
```

4. Download `--form-type` filings (write to `output/filings/--form-type`).  
*Note: restrict amount of filings per quarter via `-N` or set to sufficiently high number to download all available filings, e.g., 32,000 for 8-K, 10,000 for 10-K or 13,000 for 10-Q and extract metadata from all downlaoded filings (write to `output/filings/--form-type/metadata.csv`).*
```sh
python src/scraping.py download-filings --user-agent 'ORG_NAME MAIL_ADDRESS' --start 2020 --end 2020 --form-type 10-k -N 10000
```

### Parsing Commands

1. Preprocess filings, i.e., remove markup tags, number-heavy tables, multiple newlines, etc.  
*Note: Cleaned filing overrides the raw filing to save memory on disk. Also, it still contains markup-tags for text-heavy tables ([TABLE] ... [/TABLE]) for debugging purposes. Tags are automatically removed during information extraction in the next step.* 
```sh
python src/parsing.py clean-filings --start 2020 --end 2020 --form-type 10-k
```

2. Extract Item 1 (*Business Description*) or MD&A sections from the respective `--form-type` according to flexible, hand-coded regex patterns (write to `output/filings/--form-type` with respective file suffixes).  
*Note: Item 1 extraction is only applicable to 10-K filings.*
```sh
python src/parsing.py extract-item1 --start 2020 --end 2020 --form-type 10-k
```
```sh
python src/parsing.py extract-mda --start 2020 --end 2022 --form-type 10-k
```

### Utils

1. Helper function to sample filings from each quarter for ex post validation after setting a random seed `--seed` (write to `output/sample`).
```sh
python src/utils.py sample-filings --start 2020 --end 2022 --form-type 10-k --section-type item1 -N 4 --seed 2022
```

2. Helper function to gather all section in one large `.txt` file, with each document being delimited by a new-line (write to `output/filings/--form-type`).  
*Note: Use `--min-sec-length` to filter out short and/or corrupt sections due to parsing errors or omittance. Empirically, a minimum sequence length of 2,500 (1,500) for 10-K/10-Q MD&A (Item 1) filters out most of the edge cases.*
```sh
python src/utils.py gather-sections --form-type 10-k --section-type item1 --min-sec-length 1500
```


### Options

Find below available shorthands as well as argument default values. Check by running:
```sh
python edgar_scrape.py [-h | --help]
```

```
-h, --help
--user-agent=STR                Agent to identify with SEC EDGAR (of the form 'ORG_NAME MAIL_ADDRESS')
--start=INT                     Start year for scraping [default: 1996].
--end=INT                       End year for scraping [default: 2020].
--form-type=STR                 Form type (one of: 10-k, 10-k/a, 10-q, 10-q/a) [default: 10-k].
-N INT, --no-of-filings=INT     Number of filings to be sampled per quarter [default: 10].
--seed=INT                      Random seed for sampling [default: 2020].
--min-sec-length=INT            Minimum length of section in characters [default: 2500].
```

# Extraction Statistics for Item Boundary Detection

### 10-K: `MD&A` 1996-2020 (`n = 400`)
- *Accuarcy:* 93.25%
- *TP:* 352
- *TN:* 19
- *FP:* 0
- *FN:* 27

### 10-K: `MD&A` 2000-2020 (`n = 336`)
- *Accuarcy:* 95.54%
- *TP:* 303
- *TN:* 16
- *FP:* 0
- *FN:* 15

### 10-Q: `MD&A` 1996-2020 (`n = 400`)
- *Accuarcy:* 91%
- *TP:* 363
- *TN:* 2
- *FP:* 1
- *FN:* 34

### 10-Q: `MD&A` 2000-2020 (`n = 336`)
- *Accuarcy:* 96.4%
- *TP:* 323
- *TN:* 1
- *FP:* 0
- *FN:* 12

### 10-K: `Item 1. Business Description` 1996-2020 (`n = 400`)
- *Accuarcy:* 97.5%
- *TP:* 370
- *TN:* 20
- *FP:* 2 (incl. ToC)
- *FN:* 8

### 10-K: `Item 1. Business Description` 2000-2020 (`n = 336`)
- *Accuarcy:* 98.21%
- *TP:* 314
- *TN:* 16
- *FP:* 2 (incl. ToC)
- *FN:* 4
