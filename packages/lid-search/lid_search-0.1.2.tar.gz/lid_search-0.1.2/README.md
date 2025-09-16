# LID Search
![Version 0.1.0](https://img.shields.io/badge/version-0.1.0-blue?style=plastic)
![Language Python 3.13.2](https://img.shields.io/badge/python-3.13.2-orange?style=plastic&logo=python)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

Is a library to manage the version number of the PDS4 products coming from space missions.

## Installation

### Using pip

To install the library using pip you can use the following command:

```sh
python3 -m pip install -U pip
python3 -m pip install lid_search
```

### Using poetry

The library could be added to the poetry project using the command:

```sh
poetry add lid_serach
```

## Usage

### Database initialization

To initialize the database you can use the following instructions:

```python
>>> from lid_search import LidDB

>>> db = LidDB(jFile='input/data.json',temporary_folder='tmp',cache=False)
```

where: 
- *jFile* is the database in JSON format
- *temporary_folder* is the folder where will be stored the temporary SQLite3 database. The default is *./tmp*
- *cache* is a boolean flag and is used to eable the use a cache version of the database.

### Database interrogation

Now You can search the current version od the the lid using the *search*.

```python
>>> lid="urn:esa:psa:bc_mpo_simbio-sys:data_raw:sim_raw_sc_hric_cust0_internal_cruise_ico11_2024-04-08_001"
>>> info=db.search()
```
The output is a  [*semantic_version_tools*](https://pypi.org/project/semantic-version-tools/) class and the next version value could be obtained adding 1:

```python
>>> info 
0.1
>>> info += 1
>>> info
0.2
```

### Database closing

To close the database you can use the instructions:

```python
>>> db.close(preserve=False)
```

The keyword *preserve* is a bool that enable the preservation of the SQLite database, that could be recalled with the option *cache* in the database initialization.

