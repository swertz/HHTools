#! /bin/bash

export JAVA_HOME=/home/fynu/sbrochet/build/jdk1.8.0_102

# For bazel
export PATH=$PATH:/home/fynu/sbrochet/.local/bin

branch=v0.11.0

git clone -b ${branch} https://github.com/tensorflow/tensorflow

cd tensorflow

git apply ../tensorflow_build_fix.patch

./configure <<-EOF

N
N

N
EOF

# FIXME: tensorflow/bazel-tensorflow/external/local_config_cc/CROSSTOOL
# need to be edited in order to switch the AR tool from CMSSW
# to the system one

bazel build -c opt --jobs=30 //tensorflow/tools/pip_package:build_pip_package

bazel-bin/tensorflow/tools/pip_package/build_pip_package $PWD/..
