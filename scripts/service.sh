#!/usr/bin/env bash

cd "$(dirname "$0")" || exit
cd ../
mkdir -p ~/.config/systemd/user/
cp service/discord-bot.service ~/.config/systemd/user/
systemctl daemon-reload --user
systemctl restart queueup-bot.service --user
loginctl enable-linger $USER
exit
