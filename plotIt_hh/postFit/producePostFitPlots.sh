#!/usr/bin/env bash

get_legend() {

    local legend=""
    case $1 in
        M400)
            legend="NN output at m_{X} = 400 GeV" ;;
        M650)
            legend="NN output at m_{X} = 650 GeV" ;;
        M900)
            legend="NN output at m_{X} = 900 GeV" ;;

        1p00_1p00)
            legend="NN output at (#kappa_{#lambda}, #kappa_{t}) = (1, 1)" ;;
        5p00_2p50)
            legend="NN output at (#kappa_{#lambda}, #kappa_{t}) = (5, 2.5)" ;;
        m20p00_0p50)
            legend="NN output at (#kappa_{#lambda}, #kappa_{t}) = (-20, 0.5)" ;;

    esac

    echo $legend
}

get_legend_2d() {
    legend=$(get_legend $1)
    echo "${legend}, m_{jj} bins"
}

signals="1p00_1p00 5p00_2p50 m20p00_0p50 M400 M650 M900"

root="170319_postFitShapes"
output="170322_postFitPlots"

for signal in $signals; do

    input="${root}/${signal}/plotIt/"

    legend=$(get_legend $signal)
    legend_2d=$(get_legend_2d $signal)

    sed "s|#ROOT#|${input}|g" centralConfig_shapes_postfit.yml.tpl > centralConfig_shapes_postfit.yml

    # Uncomment signal point
    cp MCFiles_shapes_postfit.yml.tpl MCFiles_shapes_postfit.yml
    sed -i "/${signal}/,+7 s/#//" MCFiles_shapes_postfit.yml

    # MuMu

    # Replace signal and legend
    sed "s/#SIGNAL#/${signal}/g" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "s/#LEGEND_NN#/\"${legend}\"/g" postfitPlots.yml
    sed -i "s/#LEGEND_2D#/\"${legend_2d}\"/g" postfitPlots.yml
    sed -i "s/#CHANNEL#/#mu#mu channel/" postfitPlots.yml

    cp postfitPlots.yml postfitPlots_${signal}_MuMu.yml

    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    rm postfitPlots.yml

    # MuEl
    sed "s/#SIGNAL#/${signal}/g" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "s/#LEGEND_NN#/\"${legend}\"/g" postfitPlots.yml
    sed -i "s/#LEGEND_2D#/\"${legend_2d}\"/g" postfitPlots.yml
    sed -i "s/#CHANNEL#/#mue + e#mu channels/" postfitPlots.yml
    sed -i 's/MuMu/MuEl/g' postfitPlots.yml

    cp postfitPlots.yml postfitPlots_${signal}_MuEl.yml

    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    rm postfitPlots.yml

    # ElEl
    sed "s/#SIGNAL#/${signal}/g" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "s/#LEGEND_NN#/\"${legend}\"/g" postfitPlots.yml
    sed -i "s/#LEGEND_2D#/\"${legend_2d}\"/g" postfitPlots.yml
    sed -i "s/#CHANNEL#/ee channel/" postfitPlots.yml
    sed -i 's/MuMu/ElEl/g' postfitPlots.yml

    cp postfitPlots.yml postfitPlots_${signal}_ElEl.yml

    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    rm postfitPlots.yml
    rm MCFiles_shapes_postfit.yml
    rm centralConfig_shapes_postfit.yml
done

# Do ptjj & mjj for 400 GeV
for signal in M400; do

    input="${root}/${signal}/plotIt/"

    sed "s|#ROOT#|${input}|g" centralConfig_shapes_postfit.yml.tpl > centralConfig_shapes_postfit.yml

    cp MCFiles_shapes_postfit.yml.tpl MCFiles_shapes_postfit.yml

    # Uncomment signal points
    for other_signal in $signals; do
        sed -i "/${other_signal}/,+7 s/#//" MCFiles_shapes_postfit.yml
    done

    # MuMu

    # Uncomment pt jj plots
    sed "/ptjj_/,+13 s/#//" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "/mjj_/,+13 s/#//" postfitPlots.yml

    # Comment all the rest NN plots
    sed -i "/#SIGNAL#/,$ s/^/#/" postfitPlots.yml

    sed -i "s/#CHANNEL#/#mu#mu channel/" postfitPlots.yml

    cat postfitPlots.yml

    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    # MuEl

    # Uncomment pt jj plots
    sed "/ptjj_/,+13 s/#//" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "/mjj_/,+13 s/#//" postfitPlots.yml

    # Comment all the rest NN plots
    sed -i "/#SIGNAL#/,$ s/^/#/" postfitPlots.yml

    sed -i "s/#CHANNEL#/#mue + e#mu channels/" postfitPlots.yml
    sed -i 's/MuMu/MuEl/g' postfitPlots.yml
    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    # ElEl

    # Uncomment pt jj plots
    sed "/ptjj_/,+13 s/#//" postfitPlots.yml.tpl > postfitPlots.yml
    sed -i "/mjj_/,+13 s/#//" postfitPlots.yml

    # Comment all the rest NN plots
    sed -i "/#SIGNAL#/,$ s/^/#/" postfitPlots.yml

    sed -i "s/#CHANNEL#/ee channel/" postfitPlots.yml
    sed -i 's/MuMu/ElEl/g' postfitPlots.yml

    ../../../plotIt/plotIt -o ${output} -- hh_plotter_all_shapes_postfit.yml

    # Restore
    rm postfitPlots.yml
    rm MCFiles_shapes_postfit.yml
    rm centralConfig_shapes_postfit.yml
done
