#!/usr/bin/env bash

for c in MuMu MuEl ElEl; do
    for m in 400 650 900; do
        echo "Doing $m"
        rootcp --replace GluGluToRadionToHHTo2B2VTo2L2Nu_M-${m}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:jj_pt_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut               ggX0HH_M${m}_postfit_histos.root:ptjj_${c}
        rootcp --replace GluGluToRadionToHHTo2B2VTo2L2Nu_M-${m}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:jj_M_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut                ggX0HH_M${m}_postfit_histos.root:mjj_${c}
        for m2 in 400 650 900; do
            rootcp --replace GluGluToRadionToHHTo2B2VTo2L2Nu_M-${m}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:NN_resonant_M${m2}_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut    ggX0HH_M${m}_postfit_histos.root:NN_M${m2}_${c}
            rootcp --replace GluGluToRadionToHHTo2B2VTo2L2Nu_M-${m}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:flatDrop_mjj_vs_NN_resonant_M${m2}_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut    ggX0HH_M${m}_postfit_histos.root:mjj_vs_NN_M${m2}_${c}
        done
    done
    
    for m in 1p00_1p00 5p00_2p50 m20p00_0p50; do
        echo "Doing $m"
        rootcp --replace GluGluToHHTo2B2VTo2L2Nu_point_${m}_13TeV-madgraph_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:jj_pt_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut               ggHH_${m}_postfit_histos.root:ptjj_${c}
        rootcp --replace GluGluToHHTo2B2VTo2L2Nu_point_${m}_13TeV-madgraph_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:jj_M_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut                ggHH_${m}_postfit_histos.root:mjj_${c}
    
        for m2 in 1p00_1p00 5p00_2p50 m20p00_0p50; do
            rootcp --replace GluGluToHHTo2B2VTo2L2Nu_point_${m}_13TeV-madgraph_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:NN_nonresonant_point_${m2}_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut    ggHH_${m}_postfit_histos.root:NN_${m2}_${c}
            rootcp --replace GluGluToHHTo2B2VTo2L2Nu_point_${m}_13TeV-madgraph_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root:flatDrop_mjj_vs_NN_nonresonant_point_${m2}_${c}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut    ggHH_${m}_postfit_histos.root:mjj_vs_NN_${m2}_${c}
        done
    done
done
