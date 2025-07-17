Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess openzaak_new-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/openzaak_new/log/apache2/error.log"
        CustomLog "/srv/sites/openzaak_new/log/apache2/access.log" common

        WSGIProcessGroup openzaak_new-<target>

        Alias /media "/srv/sites/openzaak_new/media/"
        Alias /static "/srv/sites/openzaak_new/static/"

        WSGIScriptAlias / "/srv/sites/openzaak_new/src/openzaak_new/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-openzaak_new-<target>]
    user = <user>
    command = /srv/sites/openzaak_new/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/openzaak_new/src/openzaak_new/wsgi/wsgi_<target>.py
    home = /srv/sites/openzaak_new/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/openzaak_new/log/uwsgi_err.log
    stdout_logfile = /srv/sites/openzaak_new/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_openzaak_new_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/openzaak_new/log/nginx-access.log;
      error_log /srv/sites/openzaak_new/log/nginx-error.log;

      location /500.html {
        root /srv/sites/openzaak_new/src/openzaak_new/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/openzaak_new/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/openzaak_new/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_openzaak_new_<target>;
      }
    }
