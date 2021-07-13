#!/bin/sh

# Move to source code directory.
cd ../src

# Run unit tests
python -m unittest discover -s ../tests
