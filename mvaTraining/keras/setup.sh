#! /bin/bash

# Check if in CMSSW
if [ -n "$CMSSW_BASE" ]; then
    echo "Unfortunately, you cannot use this package inside a CMSSW environment"
    exit 1
fi  

module purge
module load python/python27_sl6_gcc49

# First, download and install pip
[ -d .python ] || mkdir .python
wget -O .python/get-pip.py https://bootstrap.pypa.io/get-pip.py
python2.7 .python/get-pip.py --no-setuptools --no-wheel --prefix=$PWD/.python

export PATH=$PATH:$PWD/.python/bin
export PYTHONPATH=$PYTHONPATH:$PWD/.python/lib/python2.7/site-packages

# Install virtualenv using pip
python2.7 .python/bin/pip --disable-pip-version-check install --prefix=$PWD/.python virtualenv

# Setup keras virtualenv
virtualenv -p $(which python2.7) --no-site-packages keras

# Move into Keras virtualenv
source keras/bin/activate

pip install numpy==1.11.2
pip install matplotlib

# Install tensorflow
TF_BINARY_URL=/home/fynu/sbrochet/build/tensorflow-0.11.0-py2-none-any.whl
pip install --upgrade $TF_BINARY_URL

pip install keras
pip install h5py
pip install pydot==1.1.0
pip install scikit-learn
pip install root_numpy

echo ""
echo "Everything is setup! Please run 'source load.sh' to switch to the new env."
