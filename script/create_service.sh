#!/bin/bash
current_dir=$(pwd)
app_name=discord-bot.service
rm -rf $app_name

cd ../
# shellcheck disable=SC2129
echo "[Unit] " >> $app_name
echo "Description=Python Script For Discord Bot" >> $app_name
echo "[Service]" >> $app_name
echo "Type = simple" >> $app_name
echo "Environment=GOOGLE_APPLICATION_CREDENTIALS=$HOME/.firebase/mwenclubhouse.json" >> $app_name
echo "ExecStart = $current_dir/main" >> $app_name
sudo cp $app_name /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/$app_name
rm $app_name
