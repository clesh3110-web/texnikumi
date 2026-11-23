#!/bin/bash
# Guliston 1-son texnikumi — Ma'lumotlar bazasi va media fayllarni avtomatik backup qilish skripti
# Har kecha soat 02:00 da crontab orqali ishlaydi

BACKUP_DIR="/var/backups/guliston_texnikum"
DATE=$(date +"%Y%m%d_%H%M%S")
DB_NAME="guliston_texnikum_db"
DB_USER="texnikum_user"

mkdir -p $BACKUP_DIR

# 1. PostgreSQL DB Dump
echo "[$(date)] PostgreSQL ma'lumotlar bazasi nusxalanmoqda..."
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > "$BACKUP_DIR/db_backup_${DATE}.sql.gz"

# 2. Media fayllarni arxivlash
echo "[$(date)] Media fayllar arxivlanmoqda..."
tar -czf "$BACKUP_DIR/media_backup_${DATE}.tar.gz" -C /var/www/guliston_texnikum media

# 3. 14 kundan eski arxivlarni tozalash
find $BACKUP_DIR -type f -name "*.gz" -mtime +14 -exec rm {} \;

echo "[$(date)] Backup muvaffaqiyatli yakunlandi: $BACKUP_DIR/db_backup_${DATE}.sql.gz"
