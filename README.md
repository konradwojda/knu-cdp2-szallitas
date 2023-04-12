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

## Run

```terminal
cd szallitas
./manage.py migrate
./manage.py createsuperuser
./manage.py load_sample_data
./manage.py runserver 8888
```

## Django Admin
You can access Django Admin site at `/admin/` and use previously set up creditentials to log in.  
There you can manage your models.  
You can also run `./manage.py shell` to run interactive interpreter.  

## Tests
Simply run tests by `./manage.py test`

## Migrations
After making any changes to model make sure to generate migrations `./manage.py makemigrations` and apply them by `./manage.py migrate`
