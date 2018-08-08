The page lists all the basic information about uploader in Nephos.

## FTP Uploads
Nephos supports uploading through FTP given all the configuration options are filled properly in `$HOME/Nephos/config/modules.yaml` and the credentials provided are correct.

FTP uploader is run before GDrive uploader but the timing for both the uploads is same and is set using the aforementioned configuration file.

## GDrive Uploader
Nephos, by default, uploads to Redhen's Drive account under the University of Navarra. The uploader module has been created keeping in mind GDrive but other cloud platforms can be added equally easily. 

To use GDrive, the admin will need to open the link provided by Nephos at it's first run, and put back the code that is received from authenticating at the link. Once authenticated, Nephos need not be authenticated again, and can be used indefinitely.

## Uploading Logs
Logs are uploaded to the same Redhen drive account under the folder `Nephos Logs` and the local logs are refreshed to start over from the point till where they've been uploaded. This has been done so that it can be accessed by anyone having access to the drive account.

All belongings of a recording, original and processed, are deleted once the upload has been completed and local space is restored.