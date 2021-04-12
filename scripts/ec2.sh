#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../
git fetch origin
git reset --hard origin/development
pip uninstall mwenclubhouse-bot -y
python3 setup.py install
cp service/discord-bot.service /lib/systemd/system/
systemctl daemon-reload
systemctl restart discord-bot.service
loginctl enable-linger $USER
exit