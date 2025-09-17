#!/bin/bash
cd /Users/areeda/ligo/python/webutils/docs
unset PYTHONPATH
. "/Users/areeda/mambaforge/etc/profile.d/conda.sh"
conda activate igwn-py39

make clean
rm -rf /Users/areeda/ligo/python/webUtils/docs/_autosummary
make html
make latexpdf

