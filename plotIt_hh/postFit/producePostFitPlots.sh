#!/usr/bin/env bash

#input="170315_postFitShapes/M900/plotIt/"
input="170315_postFitShapes/1p00_1p00/plotIt/"
output="plots_all_2017-03-15_postfit"

sed -i "s|shapes|${input}|g" centralConfig_shapes_postfit.yml

# MuMu
../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

# MuEl
sed -i 's/MuMu/MuEl/g' postfitPlots.yml
sed -i 's/#mu#mu channel/#mue + e#mu channels/g' postfitPlots.yml
../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

# ElEl
sed -i 's/MuEl/ElEl/g' postfitPlots.yml
sed -i 's/#mue + e#mu channels/ee channel/g' postfitPlots.yml
../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

# back to MuMu
sed -i 's/ElEl/MuMu/g' postfitPlots.yml
sed -i 's/ee channel/#mu#mu channel/g' postfitPlots.yml

sed -i "s|${input}|shapes|g" centralConfig_shapes_postfit.yml
