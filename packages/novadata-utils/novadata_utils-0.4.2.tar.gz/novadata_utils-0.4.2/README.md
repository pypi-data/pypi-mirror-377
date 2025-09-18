# novadata utils
Package to facilitate your day to day as a Django developer.

## Getting Started
Follow the step by step below to install and configure the package.

### Dependencies
Depends on the following packages (which will be installed automatically):

Django | Django Rest Framework | Django Admin List Filter Dropdown | Django Object Actions | Django Import Export | Django Crum.

### Installation and configuration
```shell
pip install novadata-utils
```

Settings.py:
```python
INSTALLED_APPS = [
    ...
    'django_admin_listfilter_dropdown',
    'django_object_actions',
    'import_export',
    'novadata_utils',
    'rangefilter',
    'rest_framework',
    ...
]

# After Django middlewares
MIDDLEWARE += ('crum.CurrentRequestUserMiddleware',)
```

## Features
Access the [docs](https://novadata-utils-docs.readthedocs.io/en/latest/usage.html#installation)
to see the features and how to use them.
