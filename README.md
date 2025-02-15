# Shiftings

This is a simple shift management system. Built and maintained by students from the self-governed student dormitory [HaDiKo](https://www.hadiko.de/).

## Description

This Project enables you to track Shift participation for multiple concurrent Organizations.

A Shift can either be created manually, based on a template or regularly with the use of a recurring shifts and shift templates.
A Shift template is also capable of creating multiple shifts at once.

We plan on adding functionality for managing a high density of Shifts in a short time frame. For example a 2 or 3 day event like a LAN Party.

## Getting Started

### Development / Local setup

This section describes a quick local setup for development or testing out the software running and getting accessed on a single PC.

#### Clone the repository

Start by cloning the repository and change your working directory to it:

```shell
git clone https://github.com/HaDiNet/shiftings
cd shiftings
```

#### Install dependencies

This software depends on python and its package index. The pip dependencies are listed in [pyproject.toml](pyproject.toml).

##### Manage dependencies using venv

You can manage your (virtual) python environment for this project using [venv](https://repology.org/project/python%3Avirtualenv/packages) and [pip](https://repology.org/project/python%3Apip/packages).
Make sure they are installed on your system and run the following setup commands:

```shell
python -m venv venv
source venv/bin/activate  # Linux, BSD, MacOS
# venv\Scripts\activate # Windows
pip install .
```

Make sure to activate your venv (second line above) in every shell you want to interact with your venv. Some IDEs do this automatically for you.

By running `src/manage.py` you can [run Django commands and do administration](https://docs.djangoproject.com/en/5.1/ref/django-admin/).

#### Local settings

The [project settings](src/shiftings/settings.py) are already setup for development mode (`DEBUG = True`). Feel free to have a look at the settings or adapt them to your needs. If you just want to try out the software, no action is required.

#### Database setup

The script [setup_db.sh](setup_db.sh) initializes your database with the schema matching the shiftings models (running `manage.py migrate`) and [loading the fixtures](https://docs.djangoproject.com/en/5.1/howto/initial-data/) providing example data. Execute it for having a local database:

```shell
sh setup_db.sh
```

#### Development server

Django provides a simple development server supporting live reload on code change. You can run it with the following command:

```shell
python src/manage.py runserver
```

After that you can access your local shiftings instance at <http://127.0.0.1:8000/>.

#### User fixtures

In development mode you can switch between the pre-defined user fixtures with a button in the context menu at the top right of the web page or you can login using the lower case name as username and password (`bob`, `perry` etc.). **Bob** is a superuser and has access to the [Django admin page](http://127.0.0.1:8000/admin/) and **Perry** is a staff member. The other users have [different access to the first example organization](http://127.0.0.1:8000/organizations/1/admin/) provided by the fixture. Follow the provided links for more info.

#### Upgrade Django version

View the [Django documentation for upgrading Django projects](https://docs.djangoproject.com/en/5.1/howto/upgrade-version/). After switching to an newer version, make sure there are no warnings or errors by running

```shell
 python -W all src/manage.py check --deploy
```

### Deployment / Shared setup

This section describes a shared setup deployed on a server for common use in an organization.

See [Django docs](https://docs.djangoproject.com/en/4.1/howto/deployment/) for details on how to deploy a Django application.

1. Clone the repository
1. Configure your WSGI Server
1. Add a local_settings.py. See local_settings.sample.py for inspiration.
1. Add a cron, systemd timer unit or similar for recurring shift creation

## Authors

[lewellien](https://github.com/lewellien) & [Tjeri](https://github.com/tjeri)

## License

This project is licensed under the MIT License - see the LICENSE file for details
