The page provides details on how to add data (namely jobs, channels, and share entities) to Nephos. This can be done from the runtime CLI that Nephos comes with.
***
## Basic Info
For batch operations to be performed, sample files are provided in the `config` subdirectory of Nephos directory. These should be duplicated, modified and then fed as the data file when asked for, by the CLI.
***
## Adding Jobs
### Adding Multiple Jobs
Multiple jobs can be added using the `add_jobs.yaml` file as an example. Follow the below steps in the Nephos CLI.
- `load batch jobs`
- Feed in the modified file when asked for
- The logs will notify of success/failure of the operations

**NOTE:** The recording for the job is saved in the following fashion `[JOB_NAME][%Y-%m-%d_%H%M].ts` inside its channel's directory.

### Adding A Single Job
A single job can be added using the CLI in the following manner:
- `add job`
- Provide appropriate input to the CLI prompts
- The log will notify of success/failure of the operation

## Adding Channels And Share Entities
### Adding Bulk Data
Multiple channels and share entities can be added using the `add_data.yaml` as an example. Follow the below steps in the Nephos CLI:
- `load data`
- Feed in the modified `add_data.yaml` file
- The log will notify of success/failure of the operation.

**NOTE:** If you just want to add channels or share entities, remove the other part along with the mention of the key `channels`/`jobs` in the modified file.
## Adding A Single Channel
A single channel can be added using the CLI in the following manner:
- `add channel`
- Provide appropriate input to the CLI prompts
- The log will notify of success/failure of the operation