# Auto Estate Agent

Auto Estate Agent is a Python command line program, which searches
for your new appartment or shared flat on https://www.immobilienscout24.de/
on its own according to your given search criteria.
Not only that, but it also writes a message directly to the respsective owner.
All that, fully automated and periodically repeating!

## Installation

Use the package and environment manager [conda](https://docs.conda.io/en/latest/) to install Auto Estate Agent.

```bash
conda env create -f environment.yml
```

Also set your credentials in the .env file within the settings folder.

## Usage

```bash
python estate-agent.py [-h] [-t TEXT] [-r RENT] [-s SPACE] [--shared] [--own] [-a AREA] city
```

Positional arguments:  
| city | specify where to search for a flat |
|------------|-------------------------------------|

Optional arguments:
| -h, --help | show this help message and exit |
|------------|-------------------------------------|
| -t TEXT | set the text to write to the owners |
| -r RENT | set the maximum net rent |
| -s SPACE | set the minimum living space |
| --shared | search for a shared flat |
| --own | search for your own flat (default) |
| -a | set the search area in km |
