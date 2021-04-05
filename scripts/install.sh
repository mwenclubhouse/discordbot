#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../
git fetch origin
git reset --hard origin/development
pip uninstall mwenclubhouse-bot -y
python3 setup.py install --user
exit