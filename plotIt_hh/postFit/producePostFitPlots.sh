#!/usr/bin/env bash

input=170314_postFitShapes/nonresonant_M400
output=plots_all_2017-03-14_postfit

sed -i "s|shapes|${input}|g" centralConfig_shapes_postfit.yml

# MuMu
../../plotIt/plotIt hh_plotter_all_shapes_postfit.yml -o ${output}

# MuEl
sed -i 's/MuMu/MuEl/g' postfitPlots.yml
sed -i 's/#mumu channel/#mue + e#mu channels/g' postfitPlots.yml
../../plotIt/plotIt hh_plotter_all_shapes_postfit.yml -o ${output}

# ElEl
sed -i 's/MuEl/ElEl/g' postfitPlots.yml
sed -i 's/#mue + e#mu channels/ee channel/g' postfitPlots.yml
../../plotIt/plotIt hh_plotter_all_shapes_postfit.yml -o ${output}

# back to MuMu
sed -i 's/ElEl/MuMu/g' postfitPlots.yml
sed -i 's/ee channel/#mu#mu channel/g' postfitPlots.yml

sed -i "s|${input}|shapes|g" centralConfig_shapes_postfit.yml
