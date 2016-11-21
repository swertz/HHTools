# A small toolbox to train Keras neutal networks for HH resonant & non-resonant analyses

## Installation

This package contains a set of scripts to build and train Keras neural networks for the HH resonant and non-resonant analyses. Since there's a lot of python dependencies, this package **do not work inside a CMSSW environment. Always use a clean session**.

The first thing you need to do is to install the python dependencies. This is automatically done for you using the `keras/setup.sh` script. Once again, **make sure you are not inside a CMSSW environment.**.

```bash
./keras/setup.sh
```

This script will install `pip` inside the `.python` directory, and the use this to install `virtualenv`, `keras`,`tensorflow` and a bunch of other things.

## Usage

Each time you enter this package, you need to `activate` the virtual environment. This is done by sourcing the `load.sh` script:

```bash
source load.sh
```

If everything goes fine, you should see `keras` in your bash prompt. To ensure everything is correctly setup, you can execute this command:

```bash
python -c "import tensorflow; print tensorflow.__version__"
```

which should output the version of tensorflow (currently `0.11.0`)

## Training the models

The script you need is `trainResonantModel.py`. But first, you need to edit `common.py` to set the path where to find the input ROOT files. You can also tweak the list of backgrounds considered in the NN training.
