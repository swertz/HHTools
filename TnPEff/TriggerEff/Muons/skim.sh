#! /bin/sh

input="$1"
output=$(basename $input .root)_skim.root

/afs/cern.ch/work/s/sbrochet/CP3/TnP/Muons/TnPUtils/skimTree "$input" "$output" -r "all" -k "PF Tight2012 abseta eta combRelIsoPF04dBeta dB dzPV mass pair_deltaR pt tag_IsoMu24 tag_combRelIsoPF04dBeta tag_nVertices tag_pt tag_eta tag_abseta weight *phi* DoubleIso* l1* l2* l3* Mu23*" -c "(pt > 2 && mass > 69.5 && mass < 130.1  && tag_combRelIsoPF04dBeta < 0.2 && tag_combRelIsoPF04dBeta> -0.5 && tag_pt > 23 && tag_IsoMu24==1 && abseta <2.401 && pair_probeMultiplicity == 1 && (((eta * tag_eta) > 0 && abseta > 1.2 && tag_abseta > 1.2) ? ((abs(ROOT::DeltaPhi(phi, tag_phi)) > 1.22173)) : 1))"
