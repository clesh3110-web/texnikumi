#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/var/www/guliston_texnikum"
CURRENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -f "$CURRENT_DIR/manage.py" || ! -f "$CURRENT_DIR/.env" ]]; then
  echo "XATO: loyiha ildizida manage.py va sozlangan .env bo'lishi kerak."
  echo "Avval .env.example faylini .env ga nusxalang va barcha production qiymatlarini kiriting."
  exit 1
fi

sudo apt update
sudo apt install -y python3-venv python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx rsync

sudo mkdir -p "$PROJECT_DIR"
sudo rsync -a --delete --exclude 'venv/' --exclude '__pycache__/' "$CURRENT_DIR/" "$PROJECT_DIR/"
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod 600 "$PROJECT_DIR/.env"

# PostgreSQL foydalanuvchisi mavjud bo'lmasa, parolni interaktiv so'raydi.
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='texnikum_user'" | grep -q 1; then
  sudo -u postgres createuser --pwprompt texnikum_user
fi
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='guliston_texnikum_db'" | grep -q 1 || \
  sudo -u postgres createdb -O texnikum_user guliston_texnikum_db
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE guliston_texnikum_db TO texnikum_user;"

cd "$PROJECT_DIR"
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements.txt gunicorn

sudo -u www-data venv/bin/python manage.py migrate
sudo -u www-data venv/bin/python manage.py create_initial_accounts
sudo -u www-data venv/bin/python manage.py collectstatic --noinput

sudo cp deploy/gunicorn.service /etc/systemd/system/guliston-gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable --now guliston-gunicorn

echo "Django o'rnatildi. Endi deploy/nginx.conf dagi domenlarni almashtiring, Nginx saytini ulang va Certbot bilan HTTPS yoqing."
echo "Tekshirish: sudo systemctl status guliston-gunicorn"
