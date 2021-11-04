#!/bin/sh
set -e

# DIR="execute"
DIR="execute_for_no_img"
if [ -d "$DIR" ]; then
    echo "Will be remove the diretory"
    rm -rf $DIR
    if [ $? -eq 0 ]; then
        echo "Remove the directory successfully!"
    else
        echo "Could not remove the directory"
        exit 1
    fi
fi
# pyinstaller.exe --specpath ./execute/ --distpath ./execute/dist --workpath ./execute/build --add-data "D:\Files\Project\Ptt_Crawler\crawler.ini;." -D crawler_ptt.py
pyinstaller.exe --specpath ./execute_for_no_img/ --distpath ./execute_for_no_img/dist --workpath ./execute_for_no_img/build --add-data "D:\Files\Project\Ptt_Crawler\no_img_crawler.ini;." -D crawler_ptt_no_image.py
