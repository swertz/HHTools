#!/usr/bin/env bash

# Execute this after having run the plots

if [[ "$1" == "-h" || -z "$1" ]]; then
    echo "Usage: $0 (base directory name)"
    exit 0
fi

directories=(`ls . | grep $1`)

echo "Found directories: ${directories[*]}"

for d in ${directories[*]}; do
    dir=$d/condor/output
    
    if [[ ! -d "${dir}" ]]; then
        echo "${dir} should be a valid directory"
        exit 1
    fi

    pushd $dir

    # Merge all the plotter output files
    ../hadd_histos.sh -r

    dir_content=(`ls *.root`)

    # Signal reweighting: merge the different bases together
    if [[ ${dir_content} =~ GluGluToHH.*base.*.root ]]; then 
        echo "Merging reweighted signals..."
        mergeReweightBases.sh . -r
    fi

    file_content=`rootls ${dir_content[0]}`

    # flatten 2D plots
    if [[ ${file_content} =~ mjj_vs_NN ]]; then
        echo "Flattening 2D histograms..."
        flattenTH2.py -p "flat_" -a "x" -r "mjj_vs_NN.*" -- *.root
    else
        echo "No 2D histograms found!"
    fi

    # take envelopes for scale systematics
    if [[ ${file_content} =~ scaleUncorr || ${file_content} =~ dyScaleUncorr ]]; then
        echo "Creating scale systematics..."
        createScaleSystematics.py -s scaleUncorr dyScaleUncorr -- *.root
    else
        echo "No scale systematics found!"
    fi
    
    #if [[ ${file_content} =~ dyScaleUncorr ]]; then
    #    echo "Creating DY scale systematics..."
    #    createScaleSystematics.py -s dyScaleUncorr -- *.root
    #else
    #    echo "No DY scale systematics found!"
    #fi

    echo "Done."

    popd
done

if [[ ${directories[*]} =~ $1_for_signal ]]; then echo "Moving signal files to main folder..."; mv $1_for_signal/condor/output/*.root $1/condor/output ; fi
if [[ ${directories[*]} =~ $1_for_data ]]; then echo "Moving data files to main folder..."; mv $1_for_data/condor/output/*.root $1/condor/output ; fi

## subtract MC from data for DY estimation
#pushd $1/condor/output/
#
#echo "Subtracting things for DY"
##../../../../DYEstimation/estimateDYfromData.py -d DoubleMuon* DoubleEG* --mc TTTo2L2Nu*.root ST_tW* W* Z* --dy DY*.root -o dyEstimation.root
#../../../../DYEstimation/estimateDYfromData.py -d DoubleMuon* DoubleEG* --mc TTTo2L2Nu*.root ST_tW* --dy DY*.root -o dyEstimation.root
#
#popd

if [[ ${directories[*]} =~ $1_for_signal ]]; echo "Removing empty signal folders..."; then rm -r $1_for_signal/ ; fi
if [[ ${directories[*]} =~ $1_for_data ]]; echo "Removing empty data folders..."; then rm -r $1_for_data/ ; fi
