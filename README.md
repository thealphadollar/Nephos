# Project Nephos [![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) [![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.github.com/thealphadollar/nephos/blob/master/LICENSE)
Google Summer Of Code 2018 ([![Open Source Love png3](https://badges.frapsoft.com/os/v3/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)) Project under CCExtractor; Project Nephos

# [![CodeFactor](https://www.codefactor.io/repository/github/thealphadollar/Nephos/badge)](https://www.codefactor.io/repository/github/thealphadollar/gsoc18nephos) [![Requirements Status](https://requires.io/github/thealphadollar/GSoC18Nephos/requirements.svg?branch=master)](https://requires.io/github/thealphadollar/GSoC18Nephos/requirements/?branch=master) [![Build Status](https://travis-ci.org/thealphadollar/Nephos.svg?branch=master)](https://travis-ci.org/thealphadollar/Nephos) [![codecov](https://codecov.io/gh/thealphadollar/nephos/branch/master/graph/badge.svg)](https://codecov.io/gh/thealphadollar/nephos)

## Abstract
Project Nephos aims at simplifying the process of moving samples from local storage to cloud for Universities by automating, almost, all the steps involved. It will be consisting of three independent modules; recording module, processing module, and uploading module.

The recording module will be responsible for managing the addition of channel lists, set up of recording jobs and saving the recorded streams. The processing module will parse saved samples, associate tags, extract subtitles and convert the video files to MP4 to reduce the file size. The uploading module will upload the processed stream files, and also share sample with other universities if required.

Nephos will be developed, using Python and few other open source projects, to accomplish all the above mentioned tasks with cent-percent reliability and zero failures (unless wrong data is input, which will get logged). Testing and logging will be an integral part of Nephos development and running cycle, respectively.

***
## Installation (And Setup)
1.  [Install Python3](https://kerneltalks.com/tools/install-python-3-on-linux-redhat-centos-ubuntu/)
2.1 [Install Pip](https://www.tecmint.com/install-pip-in-linux/)<br/>
2.2 [Install Multicat](https://github.com/mmalecki/multicat/blob/master/trunk/INSTALL)<br/>
3.1 [Set the following environment variables](https://www.digitalocean.com/community/tutorials/how-to-read-and-set-environmental-and-shell-variables-on-a-linux-vps) for email notifications to work.
- MAIL_HOST: Host of the mailing service, eg. for GMail, "smtp.gmail.com"
- MAIL_PORT: Port of the mailing service (for TLS connection), eg. for GMail, "587"
- CRED_EMAIL: Email address of the sender
- CRED_PASS: Password of the sender<br/>
3.2 You'll be asked to enter the email address(es) of recipient(s) of critical mails
at initialisation of Nephos. It is only asked on first launch, to edit it
later:
- Go to Nephos directory, default is $HOME/Nephos
- Edit the hidden file ".critical_mail_addrs", multiple addresses separated by
  a single whitespace
- Restart Nephos after editing the file
- In case of any email address fails at RegEx match, it'll be listed in info
  logs, ignored by config handler and you can correct it in the same file


### Install Using PyPI package
#### NOTE: This method is compromised at the moment!
4.1 Install Nephos<br/>
  `pip install nephos`<br/>
4.2 Check if the install was successful<br/>
  `nephos version`<br/>
5. Run Nephos<br/>
  `nephos start`
### Install Using Git Clone
4.1 Clone the repository<br/>
  `git clone https://github.com/thealphadollar/Nephos.git && cd Nephos`<br/>
4.2 Install Pipenv<br/>
  `pip install pipenv`<br/>
4.3 Install nephos' requirements (this step also creates a virtual environment to run nephos)<br/>
  `pipenv install`<br/>
5. Run Nephos<br/>
  `python3 -m nephos start`

## More Info
For more information regarding using Nephos and how it works, [visit the wiki](https://www.github.com/thealphadollar/Nephos/wiki)

## Reporting Bugs
Bugs should be reported in the [issue tracker](https://github.com/thealphadollar/Nephos/issues). Security issues must be reported at shivam.cs.iit.kgp+nephos@gmail.com to avoid exploitation.
