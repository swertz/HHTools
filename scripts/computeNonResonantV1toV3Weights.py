#! /bin/env python

import ROOT

v3_filename = "Distros_benchmarks_5p_500000ev_12sam_13TeV_JHEPv3.root"
# From https://github.com/acarvalh/generateHH/blob/master/mapV1/Distros_5p_500000ev_12sam_13TeV_JHEP_500K.root
#v3_filename = "Distros_5p_500000ev_12sam_13TeV_JHEP_500K.root"

#v3_filename = "GluGluToHHTo2B2VTo2L2Nu_node_{}_mhh_vs_cos_theta_star.root" #=> used for v1/v1 check

# For 1507 limits
# From https://github.com/acarvalh/generateHH/blob/master/mapV1/Distros_all_5p_20000ev_1507sam_13TeV_JHEPv3.root
v3_filename = "Distros_all_5p_20000ev_1507sam_13TeV_JHEPv3.root"

# Output of getNonResonant_gen_mhh_vs_costhetastar.py
v1_filename = "GluGluToHHTo2B2VTo2L2Nu_all_nodes_gen_mhh_vs_costhetastar.root"

def fold_cos_theta(input):
    """
    Create a new TH2 based on input, but with |cos(theta)*| instead of
    cos(theta)*
    """

    output = ROOT.TH2F(input.GetName() + "_folded", input.GetTitle(), 90, 0, 1800, 5, 0, 1)

    # Assume 5 first bins are -1 -> 0
    # Everything is hardcoded, baaaadddd but too lazy
    for i in range(0, 6):
        for j in range(0, 92):

            negative_value = input.GetBinContent(input.GetBin(j, i))
            positive_value = input.GetBinContent(input.GetBin(j, i + 5))

            # Bin 1 in input is bin 5 in output
            # Bin 2 in input is bin 4 in output
            # Etc.
            output.SetBinContent(output.GetBin(j, 6 - i), negative_value + positive_value)

    return output

v3_file = ROOT.TFile.Open(v3_filename)
v1_file = ROOT.TFile.Open(v1_filename)

v1_map = v1_file.Get("mhh_vs_abs_cos_theta_star")
v1_map_unfolded = v1_file.Get("mhh_vs_cos_theta_star")

## 1507 limits

output = ROOT.TFile.Open("weights_v1_1507_points.root", "recreate")

for point in range(0, 1507):

    # Skip dummy Xanda
    if point in [324, 910, 985, 990]: continue

    map_unfolded = v3_file.Get("%d_bin1" % point)

    # Normalize to the same integral as v1_map_unfolded
    map_unfolded.Scale(v1_map_unfolded.Integral() / map_unfolded.Integral())
    map = fold_cos_theta(map_unfolded)

    ratio = map.Clone("point_%d_weights" % point)
    ratio.Divide(v1_map)
    ratio.Write()

    ratio_unfolded = map_unfolded.Clone("point_%d_weights_unfolded" % point)
    ratio_unfolded.Divide(v1_map_unfolded)
    ratio_unfolded.Write()

    #map_unfolded.Write("point_%d_mhh_vs_cos_theta_star" % point)
    #map.Write("point_%d_mhh_vs_abs_cos_theta_star" % point)

    #v1_map_unfolded.Write("v1_all_clusters_mhh_vs_cos_theta_star")
    #v1_map.Write("v1_all_clusters_mhh_vs_abs_cos_theta_star")

output.Close()

## => used for v1/v1 check:
#for cluster in range(2, 14):
    #v3_file = ROOT.TFile.Open(v3_filename.format(cluster))
    #v3_map_unfolded = v3_file.Get("mhh_vs_cos_theta_star")
 
#for cluster in range(0, 12):
#    v3_map_unfolded = v3_file.Get("%d_bin1" % cluster)
#
#    # Normalize to the same integral as v1_map_unfolded
#    v3_map_unfolded.Scale(v1_map_unfolded.Integral() / v3_map_unfolded.Integral())
#    v3_map = fold_cos_theta(v3_map_unfolded)
#
#    output = ROOT.TFile.Open("cluster_%d_v1_to_v3_weights.root" % cluster, "recreate")
#    ratio = v3_map.Clone("weights")
#    ratio.Divide(v1_map)
#    ratio.Write()
#
#    ratio_unfolded = v3_map_unfolded.Clone("weights_unfolded")
#    ratio_unfolded.Divide(v1_map_unfolded)
#    ratio_unfolded.Write()
#
#    v3_map_unfolded.Write("v3_cluster_%d_mhh_vs_cos_theta_star" % cluster)
#    v3_map.Write("v3_cluster_%d_mhh_vs_abs_cos_theta_star" % cluster)
#
#    v1_map_unfolded.Write("v1_all_clusters_mhh_vs_cos_theta_star")
#    v1_map.Write("v1_all_clusters_mhh_vs_abs_cos_theta_star")
#
#    output.Close()
