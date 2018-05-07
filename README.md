# GSoC18Nephos
Google Summer Of Code 2018 Project under CCExtractor; Project Nephos

## Abstract
Project Nephos aims at simplifying the process of moving samples from local storage to cloud for Universities by automating, almost, all the steps involved. It will be consisting of three independent modules; recording module, processing module, and uploading module.

The recording module will be responsible for managing the addition of channel lists, set up of recording jobs and saving the recorded streams. The processing module will parse saved samples, associate tags, extract subtitles and convert the video files to MP4 to reduce the file size. The uploading module will upload the processed stream files, and also share sample with other universities if required.

Nephos will be developed, using Python and few other open source projects, to accomplish all the above mentioned tasks with cent-percent reliability and zero failures (unless wrong data is input, which will get logged). Testing and logging will be an integral part of Nephos development and running cycle, respectively.

## Mentors
@cfsmp3
@toomanybugs
