#!/bin/bash
# Turns the screen recordings in ../sources/screen into the frame folders film.html reads (fr/sanad, fr/ask).
set -e
cd "$(dirname "$0")"; mkdir -p fr/sanad fr/ask
ffmpeg -v error -y -i ../sources/screen/sanad-assistant.mov -vf "fps=30,scale=584:-1" -q:v 3 fr/sanad/%03d.jpg
ffmpeg -v error -y -i ../sources/screen/cockpit-ask.webm -vf "fps=15,crop=1329:860:0:0,scale=900:-1" -q:v 3 fr/ask/%03d.jpg
ls fr/sanad | wc -l; ls fr/ask | wc -l
