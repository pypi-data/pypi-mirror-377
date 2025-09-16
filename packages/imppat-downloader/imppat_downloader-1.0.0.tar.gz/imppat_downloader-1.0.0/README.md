## IMPPAT Downloader
[![PyPI version](https://img.shields.io/pypi/v/imppat_downloader)](https://pypi.org/project/imppat_downloader/downloader/)
[![Python](https://img.shields.io/pypi/pyversions/imppat_downloader)](https://pypi.org/project/imppat_downloader/downloader/)
[![License](https://img.shields.io/github/license/yourusername/imppat_downloader)](LICENSE)
A command-line tool to download compound structures from the IMPPAT database in bulk.
Built for researchers, bioinformaticians, and cheminformatics enthusiasts who want quick access to phytochemical structure files.

## Installation
Option 1: From source
Clone this repo and install dependencies:
```bash
git clone https://github.com/Eswar-mse/imppat_downloader.git
cd imppat_downloader
pip install -e .
```
Option 2: From PyPI (when you publish)

```bash
pip install imppat_downloader
```

## Usage
Run the tool from the command line:

```bash

imppat_downloader --start 1 --end 100 --delay 2

```

## Options

--start → first compound ID (default: 1)

--end → last compound ID (default: 10)

--delay → delay between requests in seconds (default: 2)

--skip-existing → skip already-downloaded files


## Example
Download compounds 1–50 with a 3-second delay:

```bash
imppat_downloader --start 1 --end 50 --delay 3
```
Output
- Each compound gets its own folder named by ID.
- Downloaded files include available structure formats (.sdf, .mol, .smi, etc.).
- A manifest.csv file tracks successes and failures with timestamps.


## Requirements
Python 3.8 or higher
Dependencies: requests, beautifulsoup4

## License
This project is licensed under the Apache License 2.0 – see the LICENSE file for details.

