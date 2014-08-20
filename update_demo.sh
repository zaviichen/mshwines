#!/usr/bin/env bash
#
#cd /var/www/oscar/builds/demo/
#source ../../virtualenvs/demo/bin/activate
#make demo
#
#cd sites/demo
#./manage.py thumbnail clear
#./manage.py collectstatic --noinput
#
## Re-compile python code
#touch deploy/wsgi/demo.wsgi
#
## Copy down server config files
#cp deploy/nginx/demo.conf /etc/nginx/sites-enabled/demo.oscarcommerce.com
#/etc/init.d/nginx configtest && /etc/init.d/nginx force-reload
#
#cp deploy/supervisord/demo.conf /etc/supervisor/conf.d/demo.conf
#supervisorctl reread && supervisorctl reload

set -e

echo "===> delete db file"
rm -rf db.sqlite

echo "===> syncdb & migrate"
python manage.py syncdb --noinput
python manage.py migrate

echo "===> load wine-products.json"
python manage.py loaddata fixtures/wine-products.json

echo "===> import products"
python importer.py

echo "===> import images"
python manage.py oscar_import_catalogue_images fixtures/wine-images.tar.gz

echo "===> update index"
python manage.py clear_index --noinput
python manage.py update_index catalogue
