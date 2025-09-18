# seispack: a python package for asteroseismic data analysis

## Content

[[_TOC_]] 

[//]: # (The line above generates automatically the Table of Content on gitlab.)

## Purpose

This package gather various tools useful for seismic data analysis. It is especially used by the `abim` code.

## Prerequisites

In order to install `seispack`, you will need: `numpy`, `scipy`, `matplotlib`

## Installation

For safety, we recommend to use a dedicated python environment (for example by using `pyenv` or `conda`) to avoid conflicts. Be sure that `pip` is installed, and run the following procedure:

### Installation with pip

```bash
pip install seispack
```

### Installation from gitlab of the last version

The package is available on a git repository: [gitlab.in2p3.fr/astero/seispack](https://gitlab.in2p3.fr/astero/seispack). You can download it from there or clone it:
```bash
# clone with ssh:
git clone git@gitlab.in2p3.fr:astero/seispack.git  # requires a ssh key!
# or clone with https:
git clone https://gitlab.in2p3.fr/astero/seispack.git # using login/password
```
then you can install it with pip
```bash
cd seispack
python -m pip install -e .
```
The option `-e` (for "editable") can be removed. It just links the package modules to the source. Since this code evolved quickly, each modification is immediately available without re-installation.


## Use

### `seispack` basic functions

Under construction

### Examples

Under construction

## Authors

* **Jérôme Ballot** - Maintainer - (IRAP - CNRS, Université de Toulouse)

