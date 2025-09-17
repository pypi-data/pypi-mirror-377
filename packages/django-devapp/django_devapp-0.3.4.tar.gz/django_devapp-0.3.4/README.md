# Django DevApp
Basic tools to manage a django application outside of a Django project.

Inspired from:
* ["How to Write an Installable Django App"](https://realpython.com/installable-django-app/#bootstrapping-django-outside-of-a-project).
* ["Packaging Python Projects"](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

# Depends on:

    * black
    * build
    * click
    * django
    * ipython
    * twine
    
# Help
```
$ dev --help
Usage: dev [OPTIONS]

Options:
  -a       Create Application
  -b       Run Black  [default: black]
  -bb      Build Application
  -m       Make Migrations
  -M       Migrate
  -n TEXT  The name of the application or DEVAPP_NAME env variable.
           [required]
  -pp      Upload to Pypi
  -s       Run Django Shell
  --help   Show this message and exit.

```
# Example
```
$ tree
.
├── LICENSE
├── pyproject.toml
├── README.md
└── setup.cfg

$ export DEVAPP_NAME=app
$ dev -a

$ tree
.
├── db.sqlite3
├── LICENSE
├── pyproject.toml
├── app
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── README.md
└── setup.cfg
```
