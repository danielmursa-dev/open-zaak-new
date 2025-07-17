#!/bin/bash
exec celery flower --app openzaak_new --workdir src
