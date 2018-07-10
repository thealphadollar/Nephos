#!/usr/bin/env bash

INPUT=$1
OUT_FILE_WITHOUT_EXTENSION=$2
OUT_FOLDER=$3
PATH_TO_CCEx="/home/redhen/ccextractor.0.77/linux/ccextractor"
PATH_TO_FFMPEG="ffmpeg"

cd ${OUT_FOLDER}

# extracting subtitles
${PATH_TO_CCEx} ${INPUT} -autoprogram -o ${OUT_FILE_WITHOUT_EXTENSION}.srt &> ccex.log

# compression using two pass encoding to mp4
${PATH_TO_FFMPEG} -analyzeduration 2G -probesize 2G -y -i ${INPUT} -c:v libx264 -b:v 500k -c:a copy -preset veryfast -pass 1 -f mp4 /dev/null &> ffmpeg.log
${PATH_TO_FFMPEG} -analyzeduration 2G -probesize 2G -y -i ${INPUT} -c:v libx264 -b:v 500k -c:a copy -preset veryfast -pass 2 ${OUT_FILE_WITHOUT_EXTENSION}.mp4 &>>ffmpeg.log

exit 0
