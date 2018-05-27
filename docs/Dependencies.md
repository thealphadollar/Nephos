The page provides brief details on what each of the dependency is used for in Nephos. This is a help page, aimed mostly at developers and contributors.

## Basic Info
Below are all the Nephos' dependencies:
- Pydash
- coloredlogs
- PyYAML
- click
- APScheduler
- SQLAlchemy

### PyDash
[PyDash](https://pydash.readthedocs.io/en/latest/) is used to make the process of data insertion and extraction from data types, such as python dictionary and lists, easier. An example is given below.
```python
dict1 = {
  key1: {
    "key2": value  
  }
}
print(pydash.get(dict1, "key1.key2"))
>>> value
```

### coloredlogs
[coloredlogs](https://pypi.org/project/coloredlogs/) enables colored terminal output for Python’s logging module.

![coloredlogs demo](https://warehouse-camo.cmh1.psfhosted.org/96f712ed0a5a3f3e5c6abf5791d94be99f0c4148/68747470733a2f2f636f6c6f7265646c6f67732e72656164746865646f63732e696f2f656e2f6c61746573742f5f696d616765732f64656661756c74732e706e67)

### PyYAML
[PyYAML](https://pyyaml.org/) is used to handle the loading of configuration and data files, which are in YAML format. This format has been chosen due to it's human readable asthetics and way of writing.

You can read [writing configuration files in YAML](https://martin-thoma.com/configuration-files-in-python/#yaml) for more details.

Nephos uses PyYAML's `safeload` method to load data into the program. The method forbids launching input as a script and is hence a better method than `load`.

### click
[click](http://click.pocoo.org/5/) is a Command Line Interface creation tool, and the initial interaction between User and Nephos uses the module.

### APScheduler And SQLAlchemy
[APScheduler](https://apscheduler.readthedocs.io/en/latest/), with SQLAlchemy jobstore, is used to manage the scheduling of the jobs. The [background scheduler](http://apscheduler.readthedocs.io/en/latest/modules/schedulers/background.html) from the module is used in Nephos; it stores jobs in a database permanently, and executes the tasks at designated time, all while running in the background.


