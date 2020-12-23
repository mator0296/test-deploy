#!/bin/bash
gunicorn 'mesada.wsgi' -b 0.0.0.0
