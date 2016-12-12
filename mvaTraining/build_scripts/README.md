This package contains a small script used to build tensorflow inside a CMSSW environment.

## Usage

You first need to be inside a CMSSW environment. You need to make sure that the release version you are in is the same you want to use for the analysis, otherwise there can be issue with tensorflow (ie, numpy version can change between two releases)

Once you are ready, simply execute `build-tensorflow.sh`. It'll take a while, but at the end, you should see a `whl` file in the current directory, something like `tensorflow-0.11.0-py2-none-any.whl`.

Next step is to install tensorflow with Keras so you can use them inside a CMSSW environment. To do that, simply execute `install-tensorflow.sh`. The script will install everything inside `$CMSSW_BASE/install/keras/` and will also create a small script which can be used to register tensorflow inside CMSSW, located at `$CMSSW_BASE/install/keras/add_keras_in_cmssw.sh`
