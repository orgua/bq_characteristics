# bq_characteristics

This repo contains

- measurements (raw-data)
  - efficiency measurements for buck- and boost-converter
  - recordings of internal & external state during runtime
- solar ivcurves
- capacitor charge curves
- mathematical models
- results & conclusions

for the `BQ25570`-IC.

To recreate the plots from the data you can use the provided python virtual environment (`pipenv`).

"""Shell
# to install pipenv
pip install pipenv -U

# to install environment
pipenv install

# to enter env
pipenv shell

# to exit env
exit

# for measuring there is an extended dev-environment
pipenv install -d
"""

For QA the repo is tested & linted to various tools bundled in a pre-commit.
To run it, call:

"""Shell
pre-commit run -a
"""
