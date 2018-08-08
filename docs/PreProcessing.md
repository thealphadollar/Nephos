Nephos processes the files that are downloaded using the provided stream IPs and it currently does the following;

## Convert to MP4
Nephos currently saves the recordings in `.ts` format which is not very efficient and hence we need to convert the file to MP4 using FFMPEG.

For more reasons why the file should be converted please have a look at the proposal.

## Extract Subtitles
Nephos extracts subtitles using CCExtractor and stores them along with the converted file; in fact subtitle extraction is done before conversion since in the MP4 container subtitles are lost.

# Modify Preprocessing Commands
You can easily modify preprocessing commands by opening `$HOME/Nephos/config/preprocessing.sh` and editing the file. It is advisable that while editing the file make sure that YOU KNOW WHAT YOU ARE DOING or you pose the risk of breaking the running Nephos.

A change in the file DOES NOT require Nephos to restart and the changes will take effect from the next recording.