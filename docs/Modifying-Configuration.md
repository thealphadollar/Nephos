This page provides detailed information about configuring Nephos to work according to your wishes.<br/>
BE CAREFUL WHILE MAKING ANY CHANGES!
***
## Basic Information
Nephos loads its configuration from config subdirectory from the Nephos directory in the user's home folder. Most of the configuration modifications require the client to be restarted, and those which don't have it explicitly written. Most of the changes are not recommended to be altered.<br/>

Though the configurations are stored in an easily editable `YAML` format, it is recommended to read [How to edit YAML files](http://wiki.mc-ess.net/wiki/YAML_Tutorial#YAML_Rules). In case of any violation of the YAML format, the configuration will fall back to the default configuration.
***
## logging.yaml
The configuration file concerns logging of the entire Nephos and should be modified **very carefully**. Most of the options don't need to be touched, and hence only the appropriate operations are provided in details below.
### Set Up Email Handler
The below fields are **compulsory** to fill for the working of Critical mailing service. 
- fromaddr: Address from which the mail should appear to be coming
- toaddrs: Set at the first run of Nephos
- subject: Subject of the mail, default is "[Nephos] Critical Notification"

Secondly, you need to instantiate following environment variables (before starting Nephos) for connecting and authenticating with the mailing service. **Without these, the emails won't be sent, though no exception will be raised.**
- MAIL_HOST: Host of the mailing service, eg. for GMail, "smtp.gmail.com"
- MAIL_PORT: Port of the mailing service (for TLS connection), eg. for GMail, "587"
- CRED_EMAIL: Email address of the sender
- CRED_PASS: Password of the sender

**NOTE:** If you are using GMail, you need to [enable access to Less Secure Apps](https://support.google.com/accounts/answer/6010255).
***
## maintenance.yaml
The configuration file concerns all the maintenance tasks and most of the options can be changed without an issue.
### Turning Off A Job
A job can be dynamically turned off from being executed by changing `True` to `False` in the `enabled` attribute of the  job. All jobs are enabled by default.

**NOTE:** This change takes effect immediately, no need to restart Nephos.

### Changing The Interval
A job executes periodically at the intervals provided in the configuration file. The interval can be changed by giving a new **integer** for the new period **(in minutes)** in the `interval` field of the job. The default intervals for various jobs are mentioned below:

- disk_space_check: 30 minutes
- channel_online_check: 60 minutes
- uploader_auth_check: 120 minutes
- file_upload_check: 1440 minutes (everyday at 20:00 hours)

It is recommended to give a period such that the job executes after the completion of the previous instance of the job.
### Change Minimum Disk Alert Size
For the job "disk_space_check", size to provide an alert can be set using the following two attribute:
- min_space: The minimum free space on disk, in GBs, at which to give a critical mail notice. Default is 100 GBs.
- min_percent: The minimum free percent on disk at which to give a critical mail notice. Default is 10%.

**NOTE:** The email alert depends on correctly setting up logger's emailer.
## modules.yaml
### Proper Stream Recording
Recording monitor provides two configuration options.

#### ifaddr
For the proper working of multicat, ifaddr argument should be supplied if there is a specific network interface to which it should bind.<br/>

For more info, [read here](https://github.com/mmalecki/multicat/blob/master/trunk/README).

#### path_to_multicat
Multicat is the recording client we use and it can be found [here](https://github.com/mmalecki/multicat/).<br/>
A version of multicat is bundled with the program but module can be set to use custom multicat binary by modifying this parameter.

### Proper Subtitles Extractor
For proper subtitles extraction, latest CCExtractor version should be used with appropriate arguments. The user can modify
the path to CCExtractor binary as well as the arguments to be used while extracting file using the below parameters:

- path_to_CCEx: (default is system-wide installed 'ccextractor')
- ccextractor_args: (default is '-autoprogram')

### Modifying Frequency
Preprocessing and uploading operations are launched periodicially with set intervals. These intervals can be set by modifying the paramter, `interval`
available under particular module options.

