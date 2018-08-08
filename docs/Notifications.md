This page lists all the types of Notifications that Nephos sends to the email addresses at the first start of Nephos.

## Critical Mails
These would include a detailed report of Error and he problem it causes

## Auth Failure
If due to any error or tampering of the authentication file, Nephos fails to authenticate with Google Drive, an email notification is sent to the given email addresses and Nephos exits till the error is looked upon.

## Channel Down
It happens that many a time some of the provided IPs are not online and the admin needs to be notified of the same as soon as possible. So at every check, which happens every hour, if there are new channels which are down, the admin is sent an email listing new down channels as well as channels which were previously down.

## Low Disk Space
In case the space on the disk goes below the critical disk space specified in the configuration files, a mail is sent detailing the available space and the amount by which it is less than the recommended.

## Configuration Update
Whenever configuration is changed at the linked "NephosConfig" repository, an email notification is sent making the admin and others aware whether the new Data was added successfully or not. Errors are logged in case of failure.

## Daily Reports
These are detailed reports which are sent once in a day: contains all the recordings that were uploaded, skipped due to some error and FTP uploads as well. Most of the skippings will contain the reason but it is advisable to look into the logs in case of repetitive problems.