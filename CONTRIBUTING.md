Thank you for considering contributing to Nephos and helping Redhen move one step further towards automation. It is vital that you read the 
below given details to let the process of contributing and maintaining remail hassle-free.

## Documentation
If you are looking forward to contribute, please have a look at the issues tab and then open the concerned file(s) docstring using the developer's 
documentation present in `docs/DevDocs`. If you are trying to implent a new feature, it is pivotal to first read the user docs, 
`docs/UserDocs.html` and then navigate through the developer documentation to find the right spot where your feature will be added.

All documentation exists inside the `docs` folder and on the Wiki of the repository. The documentation is exhaustive and in case of any
discrepencies please create an issue or mail to `shivam.cs.iit.kgp+nephos@gmail.com`.

## Code Quality
Nephos has been made in a modular fashion and [flexible] functional programming (with Object Oriented Programming) has been used to do implement all modules and methods.
It is obvious that we expect the same to be continued and hence, we would like your code to be following the module and functional approach.

- All configuration related code/text goes to `default_config` folder.
- All preprocessor related code goes to `preprocessor` folder and shall be embedded inside `PreProcessHandler`.
- All recorder related code goes to `recorder` folder and shall be embedded inside the same module.
- All uploader related code goes to `uploader` folder and shall be embedded inside the same module.

Follow the guidelines of PEP8 while writing code and implement all the changes suggested by CodeCov after you've sent the PR.

DocStrings should be present for all new functions you add, and accordingly the DevDocs and UserDocs should be updated (in separate commits).
DevDocs is created using `PyDoc` and UserDocs.html is created using [`github-wikito-converter`](https://www.npmjs.com/package/github-wikito-converter).

DO NOT TAMPER THE DIRECTORY STRUCTURE AT ANY COST.

## Code Review
You've to understand that reviewing your PR may take anywhere from a couple of days to couple of weeks. Nephos is an all time running
client and it cannot take the blunt of stopping due to any unforeseen bug. Hence we would like you to have patience while we review
your code and test it locally/remotely before deploying the change onto the main server.

## Thank You For Your Love To Open Source
