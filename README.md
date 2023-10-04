# CS4211-NFL-Project

## Setup

### Virtual Environment
Run `python -m venv .venv` to create a virtual environment.
Run `./venv/Scripts/Activate.ps1` to activate the virtual environment.

### Dependencies
Run `pip install -r requirements.txt` to install dependencies.

## Data Processing

### Input Data
Place the input data in the `./dataset` folder.

### Preprocessing
Run `python ./processing/main.py` to preprocess the data. 
The processed data will be output to `./output/{TEAM}.xlsx`.
Be sure to change the `TEAM` variable in `main.py` to the team you want to process.
