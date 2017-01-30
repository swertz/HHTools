#!/usr/bin/env bash

# Execute this after having run the main plots

# exit if any command fails
set -e

if [[ "$1" == "-h" || -z "$1" ]]; then
    echo "Usage: $0 (base directory name)"
    exit 0
fi

for dir in $1/condor/output $1_for_signal/condor/output $1_for_data/condor/output; do
    if [[ ! -d "${dir}" ]]; then
        echo "${dir} should be a valid directory"
        exit 1
    fi

    pushd $dir

    # Merge all the plotter output files
    ../hadd_histos.sh -r

    # Signal reweighting: merge the different bases together
    if [[ `ls` =~ .*GluGluToHH.*base.*.root ]]; then ../../../../scripts/mergeReweightBases.sh . -r ; fi

    # flatten 2D plots
    flattenTH2.py -p "flat_" -a "x" -r "mjj_vs_NN.*" -- *.root

    # take envelopes for scale systematics
    createScaleSystematics.py -s scaleUncorr dyScaleUncorr -- *.root

    popd
done

mv $1_for_signal/condor/output/*.root $1/condor/output
mv $1_for_data/condor/output/*.root $1/condor/output

# subtract MC from data for DY estimation
pushd $1/condor/output/

../../../../DYEstimation/estimateDYfromData.py -d DoubleMuon* DoubleEG* --mc TTTo2L2Nu*.root ST_tW* W* Z* --dy DY*.root -o dyEstimation.root
#../../../../DYEstimation/estimateDYfromData.py -d DoubleMuon* DoubleEG* --mc TTTo2L2Nu*.root ST_tW* --dy DY*.root -o dyEstimation.root

popd

rm -r $1_for_signal
rm -r $1_for_data
