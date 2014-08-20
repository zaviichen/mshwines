set -e

echo "===> dgango settings..."
python manage.py thumbnail clear
python manage.py collectstatic --noinput

echo "===> start nginx..."
rm -r /etc/nginx/sites-enabled/mshwines.conf
ln -s /root/www/mshwines/deploy/mshwines.conf /etc/nginx/sites-enabled/mshwines.conf
/etc/init.d/nginx configtest
/etc/init.d/nginx force-reload

echo "===> start uwsgi..."
uwsgi -x deploy/uwsgi.xml

echo "===> start successfully!"