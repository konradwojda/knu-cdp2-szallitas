# SZALLITAS - Easy Transport Management System

## Installation

```terminal
git clone git@github.com:konradwojda/knu-cdp2-szallitas.git szallitas
cd szallitas
sudo apt update && sudo apt install python3 python3-venv  # Install Python 3 and its venv module
python3 -m venv .venv                 # Create a Python virtual environment
source .venv/bin/activate             # Enter the virtual environment
pip install -U pip wheel setuptools   # Update the virtual environment
pip install -Ur requirements.dev.txt  # Install project dependencies
```
