Welcome to the Nephos wiki!

Here you can find all the information required to setup, configuration and running of Nephos on your system.
***
## Abstract
Project Nephos aims at simplifying the process of moving samples from local storage to cloud for Universities by automating, almost, all the steps involved. It will be consisting of three independent modules; a recording module, processing module, and uploading module.

The recording module will be responsible for managing the addition of channel lists, set up of recording jobs and saving the recorded streams. The processing module will parse saved samples, associate tags, extract subtitles and convert the video files to MP4 to reduce the file size. The uploading module will upload the processed stream files, and also share the sample with other universities if required.

Nephos will be developed, using Python and few other open source projects, to accomplish all the above-mentioned tasks with cent-percent reliability and zero failures (unless wrong data is input, which will get logged). Testing and logging will be an integral part of the Nephos development and running cycle, respectively.
***
## Installation (And Setup)
1.  [Install Python3](https://kerneltalks.com/tools/install-python-3-on-linux-redhat-centos-ubuntu/)<br/>
2. 1) [Install Pip](https://www.tecmint.com/install-pip-in-linux/)<br/>
   2) [Install Multicat](https://github.com/mmalecki/multicat/blob/master/trunk/INSTALL)<br/>
3. 1) [Set the following environment variables](https://www.digitalocean.com/community/tutorials/how-to-read-and-set-environmental-and-shell-variables-on-a-linux-vps) for email notifications to work.
        - MAIL_HOST: Host of the mailing service, eg. for GMail, "smtp.gmail.com"
        - MAIL_PORT: Port of the mailing service (for TLS connection), eg. for GMail, "587" 
        - CRED_EMAIL: Email address of the sender
        - CRED_PASS: Password of the sender<br/>
   2) You'll be asked to enter the email address(es) of recipient(s) of critical mails
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
4. 1) Install Nephos, `pip install nephos`<br/>
   2) Check if the install was successful, `nephos version`<br/>
5. Run Nephos, `nephos start`
### Install Using Git Clone
4. 1) Clone the repository, `git clone https://github.com/thealphadollar/Nephos.git && cd Nephos`<br/>
   2) Install Pipenv, `pip install pipenv`<br/>
   3) Install nephos' requirements (this step also creates a virtual environment to run nephos), `pipenv install`
5. Run Nephos `python3 -m nephos start`

## Reporting Bugs
Bugs should be reported in the [issue tracker](https://github.com/thealphadollar/Nephos/issues). Security issues must be reported at shivam.cs.iit.kgp+nephos@gmail.com to avoid exploitation.
***
# **This wiki is a work in progress!**

