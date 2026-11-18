cd "$(dirname "$0")"
pkill -f "python app.py"; sleep 1; rm -rf app/instance
(cd app && PHARMACY_DEV=1 PHARMACY_ADMIN_PASSWORD=admin-pass-123 setsid nohup /home/user/pharmacy-pos-cockpit/.venv/bin/python app.py > ../server.log 2>&1 < /dev/null &)
sleep 4; node probe.js >/dev/null && node rec.js "$@"
