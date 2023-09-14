#!/usr/bin/bash

# The path to the folder containing the virtual environment
venv_dir=

# The name of your virtual environment
venv_name="venv"

# Checking if the venv folder exists
if [ ! -d "$venv_dir" ]; then
  eho "The virtual environment does not exist at the specified location."
  exit 1
fi

# Activating the virtual environment
source "$venv_dir/$venv_name/bin/activate"

echo "The $venv_name virtual environment has been activated."

screen -dmS api_yoocard uvicorn app.main:app --host localhost --port 9000

echo "The server has been successfully launched."