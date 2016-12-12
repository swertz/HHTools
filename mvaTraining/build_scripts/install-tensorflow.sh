#! /bin/bash

# Check if in CMSSW
if [ -z "$CMSSW_BASE" ]; then
    echo "You must use this package inside a CMSSW environment"
    exit 1
fi  

# First, download and install pip
[ -d .python ] || mkdir .python

if [ ! -f .python/bin/pip ]; then
    wget -O .python/get-pip.py https://bootstrap.pypa.io/get-pip.py
    python2.7 .python/get-pip.py --prefix=$PWD/.python
fi

export PATH=$PATH:$PWD/.python/bin
export PYTHONPATH=$PWD/.python/lib/python2.7/site-packages:$PYTHONPATH

# Install tensorflow
TF_BINARY_URL=$PWD/tensorflow-0.11.0-py2-none-any.whl
python2.7 .python/bin/pip install --prefix=${CMSSW_BASE}/install/keras --no-deps --upgrade $TF_BINARY_URL

# Install h5py
python2.7 .python/bin/pip install --prefix=${CMSSW_BASE}/install/keras --no-deps --ignore-installed --upgrade h5py

# Install Keras
python2.7 .python/bin/pip install --prefix=${CMSSW_BASE}/install/keras --no-deps --ignore-installed --upgrade Keras

# Tool xml
mkdir -p tools_xml

# root_interface toolfile
cat <<EOF_TOOLFILE >tools_xml/keras_with_tensorflow.xml
<tool name="keras" version="0.11.0">
  <info url="https://keras.org"/>
  <client>
    <environment name="KERAS_BASE"         default="${CMSSW_BASE}/install/keras"/>
    <environment name="LIBDIR"             default="\$KERAS_BASE/lib/"/>
    <runtime name="PATH"                   value="\$KERAS_BASE/bin" type="path"/>
    <runtime name="PYTHONPATH"             value="\$KERAS_BASE/lib/python2.7/site-packages" type="path"/>
  </client>

  <use name="py2-six"/>
  <use name="py2-numpy"/>
  <use name="py2-scipy"/>
  <use name="py2-scikit-learn"/>
</tool>
EOF_TOOLFILE

cat >add_keras_in_cmssw.sh <<EOF 
scram setup $PWD/tools_xml/keras_with_tensorflow.xml
EOF
chmod +x add_keras_in_cmssw.sh
mv add_keras_in_cmssw.sh ${CMSSW_BASE}/install/keras/
