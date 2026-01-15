#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. ลง Library ตามใบสั่ง
pip install -r requirements.txt

# 2. รวบรวมไฟล์ Static (CSS/JS)
python manage.py collectstatic --no-input

# 3. สร้างตารางใน Database
python manage.py migrate