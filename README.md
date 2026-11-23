# GULISTON 1-SON TEXNIKUMI

Django asosidagi ta'lim muassasasini boshqarish platformasi.

## Tarkibi
- `apps/accounts` — foydalanuvchilar, autentifikatsiya va rollar
- `apps/students`, `apps/teachers` — talaba va o'qituvchi profillari
- `apps/groups`, `apps/subjects` — guruhlar va fanlar
- `apps/journal`, `apps/attendance` — baholar va davomat
- `apps/timetable`, `apps/assignments` — jadval va topshiriqlar
- `apps/documents`, `apps/library` — hujjatlar va kutubxona
- `apps/messaging`, `apps/notifications` — xabarlar va bildirishnomalar
- `apps/reports`, `apps/audit` — hisobotlar va audit
- `templates`, `static` — foydalanuvchi interfeysi

## Muhim
Arxivda demo foydalanuvchilar, demo ma'lumotlar bazasi, maxfiy `.env` yoki yuklangan test hujjatlari mavjud emas.
Birinchi ishga tushirishda toza baza yaratiladi va har bir rol uchun bittadan hisob ochiladi.
Haqiqiy talabalar, guruhlar, fanlar, baholar, davomat va jadval ma'lumotlarini administrator kiritadi.
Bo'sh bazada modullar ma'lumot ko'rsatmaydi — bu normal holat.

## Windows'da mahalliy ishga tushirish

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` faylida `SECRET_KEY` va to'rtta `INITIAL_*_PASSWORD` qiymatini o'zgartiring.
Mahalliy sinov uchun `DEBUG=True`, `ALLOWED_HOSTS=127.0.0.1,localhost`,
`CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000` belgilang
va `DB_ENGINE=sqlite3` qiling.

```powershell
python manage.py migrate
python manage.py create_initial_accounts
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/

## Ubuntu VPS / Production

1. Domenni VPS IP manziliga yo'naltiring.
2. Ubuntu serverga Python, PostgreSQL, Nginx va Git o'rnating.
3. Loyihani `/var/www/guliston_texnikum` ichiga joylashtiring.
4. `.env.example` nusxasini `.env` deb nomlang va production qiymatlarini kiriting:
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.uz,www.your-domain.uz`
   - `CSRF_TRUSTED_ORIGINS=https://your-domain.uz,https://www.your-domain.uz`
   - PostgreSQL ulanish ma'lumotlari
   - `SECRET_KEY` uchun `get_random_secret_key()` natijasi
   - to'rtta boshlang'ich rol paroli
5. `.env` ruxsatini cheklang: `chmod 600 .env`.
6. Virtual muhitni yarating, `pip install -r requirements.txt gunicorn`, so'ng:

```bash
python manage.py migrate
python manage.py create_initial_accounts
python manage.py collectstatic --noinput
```

7. `deploy/nginx.conf` ichidagi `YOUR_DOMAIN` va `YOUR_WWW_DOMAIN` ni haqiqiy domen bilan almashtiring.
8. Nginx konfiguratsiyasini ulang:

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/guliston_texnikum
sudo ln -sfn /etc/nginx/sites-available/guliston_texnikum /etc/nginx/sites-enabled/guliston_texnikum
sudo nginx -t
sudo systemctl reload nginx
```

9. SSL oling: `sudo apt install -y certbot python3-certbot-nginx`, so'ng `sudo certbot --nginx -d your-domain.uz -d www.your-domain.uz`.
10. SSL tayyor bo'lgach `.env` ichida `SECURE_SSL_REDIRECT=True` qiling va `sudo systemctl restart guliston-gunicorn` bajaring.
11. Boshlang'ich hisoblar yaratilgach, `INITIAL_*_PASSWORD` qiymatlarini `.env` dan olib tashlang.
12. Zaxira nusxalarini muntazam oling.

## Buyruqlar

```bash
python manage.py check
python manage.py check --deploy
python manage.py test apps
```

Testlar ichidagi sinov foydalanuvchilari faqat test muhiti uchun; ular production bazasiga yuklanmaydi.
