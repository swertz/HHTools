#!/usr/bin/env bash

# Usage: './mergeReweightBases.sh condor_output_folder [-r]'

# Merge reweighted signal samples which have different bases:
# For each target point of the grid, do the hadd of all the output files corresponding to that point.
# This assumes the reweighting took into account this step, by e.g. dividing the weights by the number of base samples
# The script assumes the samples are named 'GluGluToHHTo2B2VTo2L2Nu_base_BASE_point_POINT_13TeV*.root'
# If asked, remove base files.

pushd $1

search_regex='./GluGluToHHTo2B2VTo2L2Nu_base_.*_point_.*.root'

bases_list=(`find -regex ${search_regex} -printf "%f\n" | sed 's/GluGluToHHTo2B2VTo2L2Nu_base_\(.*\)_point_.*.root/\1/g' | sort | uniq`)
point_list=(`find -regex ${search_regex} -printf "%f\n" | sed 's/GluGluToHHTo2B2VTo2L2Nu_base_.*_point_\(.*\)_13TeV.*.root/\1/g' | sort | uniq`)
name_suffix=(`find -regex ${search_regex} -printf "%f\n" | sed 's/GluGluToHHTo2B2VTo2L2Nu_base_.*_point_.*_13TeV//g' | sort | uniq`)

if (( ${#bases_list}==0 || ${#point_list}==0 )); then
    echo "Could not parse file names!"
    exit 1
fi

for point in ${point_list[*]}; do
    new_name=GluGluToHHTo2B2VTo2L2Nu_point_${point}_13TeV${name_suffix}
    hadd ${new_name} GluGluToHHTo2B2VTo2L2Nu_base_*_point_${point}_*.root && { if [ "$2" == "-r" ]; then rm GluGluToHHTo2B2VTo2L2Nu_base_*_point_${point}_*.root; fi }
done

popd
