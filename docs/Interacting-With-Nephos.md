Nephos provides a minimal CLI to interact with it at the runtime. All the options are explained below. To interact with other parts of Nephos, configuration files are provided and, details are available on `Modifying Configuration` page.

## Basic Info
Below is a screenshot of the help screen of the CLI.

![CLI help](https://preview.ibb.co/hBiv8J/Screenshot_from_2018_05_27_22_50_32.png)

### Adding Data
The CLI provides options to add data to Nephos. This has been explained in "Adding Jobs, Channels, And Share Entities" page in details. 

### Viewing Data 
Currently added channels, jobs and share lists can be listed using the below options respectively.
- `list channels`: Lists all the currently added channels with their details
- `list jobs`: Lists all the pending jobs with their id and next-run's time.

### Removing Data
Jobs, Share lists, and Channels can be removed using the following options.
- `remove channel`: Remove channel by entering its name or IP
- `remove job`: Remove job by using its ID

**NOTE:** It is advised to list data and verify ID/Name before trying to use remove.
