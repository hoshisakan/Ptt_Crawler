#!/bin/sh
set -e

DIR="execute"
if [ -d "$DIR" ]; then
    echo "Will be remove the diretory"
    rm -rf execute
    if [ $? -eq 0 ]; then
        echo "Remove the directory successfully!"
    else
        echo "Could not remove the directory"
        exit 1
    fi
fi
pyinstaller.exe --specpath ./execute/ --distpath ./execute/dist --workpath ./execute/build --add-data "D:\Files\Project\Ptt_Crawler\crawler.ini;." -D crawler_ptt.py