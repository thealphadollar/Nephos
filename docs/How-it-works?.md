An overview of the working of Nephos has been explained. The code for the same has been documented appropriately and developers can use this as a reference for understanding it better.
***
## Starting Nephos
Once Nephos is installed into the system, it can be started `nephos start` or `python3 -m nephos start` depending on the method of installation.<br/><br/>
To get information about the module version and author, `nephos version` or `python3 -m nephos version`. The command displays the following information:
- __title__ <br/>
- __description__ <br/>
- __author__ <br/>
- __author_mail__ <br/>
- __license__ <br/>
- __version__ <br/>
- __release__ <br/>

As soon as Nephos is started, a check for another instance of the same is done and if another running nephos is identified, the program quits (details at the end). If this is the only running Nephos, the logger is configured using the configuration file (see the configuration page). Moving on, database, scheduler, and maintenance module are initialized. For all this, configuration files are loaded into the program from config subdirectory (see below).

### First Run
If it is the first time that Nephos has been run on the system, the client creates create the directory Nephos and it's following subdirectories in user's home directory.
- config: contains user-editable configuration files
- logs: store log information in text
- databases: stores the database for Nephos
- recordings: stores the recorded streams
- processed: stores processed mp4 files and associated files in directories to be uploaded<br/>

### Configuring Logger
Logger is the first part of Nephos that is configured and brought to life since reporting of most of the errors and information depends on it.<br/><br/>
As stated in the configuration file `logging.yaml`, logging is handled in multiple ways; there is reporting in the console window for informational logs and then there are separate log files for different modules which store even the debugging logs. On top of all, there is an email handler which sends a mail for all critical logs to the specified address in the configuration file.<br/><br/>
**NOTE:** Email handler depends on environment variables for working, more details on the configuration page.

### Database Initialisation
If Nephos has been run the first time, by default two database files are created to store channels and share lists, and jobs respectively. The below storage paths can be changed, to some extent, but it is advisable to follow the default config.
- Channel and share lists (default): `$HOME/nephos/databases/storage.db`
- Jobs (default): `$HOME/nephos/databases/jobs.db`<br/>

Two tables are created for Channels and Share entities in `storage.db`. Channels are indexed using their IP address and share lists are indexed using email addresses. Following are the columns available in these tables, the details about them are provided in adding data section.<br/>

##### Channels
- channel_id 
- name 
- ip
- country_code 
- lang
- timezone
- status
##### Share lists
- share_id,
- email
- channel_name 
- country_code
- lang 
- timezone<br/>

Except at the first run of Nephos, database operations remain inactive unless invoked by the runtime commands. 

### Scheduler Initialisation
Nephos uses a background Scheduler with SQLAlchemy to store and run jobs from a database of jobs, stored permanently. This method allows Nephos to keep the stored job even at a restart of the entire system, carrying forward all the jobs that were added and also notifies of the jobs that have been missed due to the inactive scheduler.<br/>

The scheduler can at max have 20 jobs running concurrently, and the default timezone is set automatically using the system timezone. A fallback to "UTC" timezone is done if the system timezone is unrecognized.<br/>

The scheduler keeps running in the background while the program is active and executes jobs, detailing about them through logs.

### Channels And Jobs Handler
Channels and Jobs operations initiated during the runtime of Nephos are handled by these two passive classes. They provide a link to work with the database and scheduler; listing and inserting new data.

### Maintenance Jobs' Initialisation
Maintenance jobs are used to ensure the safe and error-free working of Nephos. This is done via having multiple periodic checks and providing a report of them over the provided mail address in critical cases.

At the start, it loads configuration from the config file `maintenance.yaml` and passes configuration to the concerned jobs, which are:
-**call_disk_space_check:** To check if the disk space is less than a minimum threshold defined in the config file
-**call_channel_online_check:** To check the status of channels, whether online or not
***
## Nephos Runtime
Nephos is kept running in the terminal using a while loop after starting the scheduler. The loop also facilitates the incorporation of a CLI into the runtime, hence making the addition of channels and jobs dynamic. Logs are made available in the terminal itself, alongside CLI, which can be confusing at times. Nonetheless, any supported CLI command (detailed on `interacting with nephos` page) can be entered at any point of runtime.

Nephos can be shut down by giving `quit/exit` command during the runtime; it'll let any of the pending jobs complete and then exit.

### Interacting With Nephos
Nephos provides a minimalistic CLI while it's running. More information and methods to interact with the module are given on `Interacting With Nephos` page.

### Channels, Share Entities And Jobs
New data can be entered in Nephos, at runtime only, using the CLI. 

As soon as a new channel is added in Nephos, a directory for the channel is created in the `recordings` subdirectory of Nephos folder. This directory is used to store jobs concerning the channel. 

When a job is launched, it checks the status of the associated channel. If the channel is "up" (was online at the time of last test), the job executes. Once the recording has started, the data received is stored in a file named `[JOB_NAME][DATE-TIME].ts` in the channel's folder. 

The entry in sharing entities is used by the uploader to add them to the share list of the file during upload.

**NOTE:** Nephos uses ["multicat"](https://www.videolan.org/projects/multicat.html) for recording streams to the file.
***
**NOTE**<br/>

Only a single instance of Nephos can be run at a time, this is done by using a [PID file and locking](https://stackoverflow.com/questions/380870/python-single-instance-of-program) onto it when the code is running. This is done in order to avoid multiple errors but the major one is having two schedulers running at the same time. Two schedulers at the same time can mess up with the recording and also cause malfunctioning of preprocessing and uploading modules.