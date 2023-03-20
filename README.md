[![GitHub issues](https://img.shields.io/github/issues/SentioProberDev/SentioProberControl.svg?maxAge=360)](https://github.com/SentioProberDev/SentioProberControl/issues)
[![Version](https://img.shields.io/github/release/SentioProberDev/SentioProberControl.svg?maxAge=360)](https://github.com/SentioProberDev/SentioProberControl/releases/)
[![Github All Releases](https://img.shields.io/github/downloads/SentioProberDev/SentioProberControl/total.svg)](https://github.com/SentioProberDev/SentioProberControl/releases/)
# SENTIO® Prober Control - Python Bindings
This archive contains a package with python bindings to control a [MPI SENTIO® probe station](https://www.mpi-corporation.com/ast/engineering-probe-systems/mpi-sentio-software-suite/).

![AST_Back_2A fw_](https://user-images.githubusercontent.com/2202567/204108957-0c7a864a-a526-4d32-a1ca-51985a0b01c6.png)

## Instructions for installing the SENTIO® prober control Python package

The package for controlling MPI probe stations running the MPI SENTIO Software suite is now available via pythons package index. To install the
package simply type:

```python -m pip install sentio-prober-control```

## Example-Scripts

A set of example scripts for python is maintained in a seperate archive at GitHub. 

https://github.com/SentioProberDev/Examples-Python

## Troubleshooting

If you have problems getting the package to work. Check wether an old version of the sentio-prober-control is still installed. To do so type

```python -m pip list```

if an older version is listed uninstall it first by using the command. 

```python -m pip uninstall sentio-prober-control```

After the uninstallation you can proceed with the installation as explained in the section above.

## Instructions for package maintainer (updating the package) 

*This section is for the package maintainers at MPI Corporation. The following instructions are for creating a new release of the package. If you only want to use the package you do not need to do this! Just follow the instructions listed above for installing an existing package.*

1.) Get the latest version of setuptools and wheel:

```python -m pip install --user --upgrade setuptools wheel```

2.) Update the package Version number

Open the file setup.py an change the "version" attribute to the most current version of SENTIO tested with the python package. The python package is backwards
compatible and will run with older SENTIO versions in general but it may contain new API bindings that are missing in the old versions.

3.) create the distribution archive:

cd into the archive (where setup.py) is located.

```python setup.py sdist bdist_wheel```

This command will create the dist folder.

```
dist/
  sentio-prober-control-3.8.0-py3-none-any.whl
  sentio-prober-control-3.8.0.tar.gz
```

4.) Create a new release on GitHub with the new binary archive

Make sure to manually add the created python package to the release.
