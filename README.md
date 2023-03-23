# Shiftings

This is a simple shift management system. Built and maintained by students from the self-governed student dormatory [HaDiKo](https://www.hadiko.de/).

## Description

This Project enables you to track Shift participation for multiple concurrent Organizations.

A Shift can either be created manually, based on a template or regularly with the use of a recurring shifts and shift templates.
A Shift template is also capable of creating multiple shifts at once.

We plan on adding functionality for managing a high density of Shifts in a short time frame. For example a 2 or 3 day event like a LAN Party.

## Getting Started

### Requirements

* Python >= 3.9
* Gunicorn or similar WSGI/ASGI Server

### Installing

See [django docs](https://docs.djangoproject.com/en/4.1/howto/deployment/) for details on how to deploy a django application.

1. Clone the repository
1. Configure your WSGI Server
1. Add a local_settings.py. See local_settings.sample.py for inspiration.
1. Add a cron, systemd timer unit or similar for recurring shift creation


## Authors

[lewellien](https://github.com/lewellien) & [Tjeri](https://github.com/tjeri)

## License

This project is licensed under the MIT License - see the LICENSE file for details
