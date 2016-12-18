#! /bin/env python

from __future__ import division

import argparse
import os
import sys
from array import array

import numpy as np

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'bin', SCRAM_ARCH))

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

from SAMADhi import Dataset, Sample, File, DbStore

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.Reset()

parser = argparse.ArgumentParser(description='Compute b-tagging efficiency on a given sample')
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-d', '--json', type=str, metavar='FILE', help='JSON file describing the input')
group.add_argument('-i', '--id', type=int, metavar='ID', help='Sample ID')
group.add_argument('-n', '--name', type=str, metavar='STR', help='Sample name')

parser.add_argument('dummy', type=str, help="Dummy argument for compatibility with condorTools")

options = parser.parse_args()

def get_sample(id=None, name=None):
    store = DbStore()
    if (id):
        result = store.find(Sample, Sample.sample_id == id)
    else:
        result = store.find(Sample, Sample.name == unicode(name))

    return result.one()

cross_section = 0
event_wgt_sum = 0

if options.json:
    import json
    with open(options.json) as f:
        data = json.load(f)
        data = data[data.keys()[0]]
        files = data["files"]
        cross_section = data["cross-section"]
        event_wgt_sum = data["event-weight-sum"]
    entries = None
else:
    storage_root = '/storage/data/cms'
    sample = get_sample(options.id, options.name)
    files = []
    for file in sample.files:
        files.append(storage_root + file.lfn)
        event_wgt_sum += file.event_weight_sum
    cross_section = sample.source_dataset.xsection
    entries = sample.nevents

output = "dy_flavor_fraction.root"

#### 161212, 8 var, incl. vs. bb
# 50 bins
#binning = np.asarray(
#        [-0.4221516067578435, -0.2492364543069245, -0.2174758533355315, -0.1950796433528712, -0.17592908619139971, -0.15922232890015742, -0.14504348368871342, -0.13274378645423165, -0.12137735682180249, -0.11085927132395268, -0.10082988895715296, -0.09111207435262407, -0.08203581262875936, -0.07316461157264477, -0.0650314607985117, -0.05718383291674172, -0.04971423426838821, -0.042684807749649625, -0.03597067907321709, -0.029427859305389815, -0.02313143978259138, -0.017071092038303665, -0.01124685192313947, -0.005440469068357586, 0.00015178708522947627, 0.005690815269577133, 0.010989482724455069, 0.016066454265181544, 0.02124198177005059, 0.026253843607455626, 0.031157806287590756, 0.03618101567523746, 0.04107440300922436, 0.04550256610101927, 0.05027682822637862, 0.05498237458280163, 0.05969966412782347, 0.06435968246605253, 0.06913450905675347, 0.07393806287695635, 0.07896111101514787, 0.08404007636624614, 0.08957661755046453, 0.09521771711292036, 0.10123364060428733, 0.10784451063421104, 0.115070280211909, 0.1235694846358312, 0.13396788576729096, 0.1498792525644745, 0.28486487478573513]
#        , dtype='float')

# 30 bins
#binning = np.asarray([
#-0.4221516067578435, -0.22642553811280164, -0.18854184240353225, -0.1592223289001575, -0.13655754048267943, -0.1177293064928864, -0.10082988895715302, -0.08494772483024618, -0.07046480520683986, -0.05718383291674184, -0.04494896849077846, -0.033692287241319153, -0.0231314397825901, -0.013222139106947216, -0.003522534240713981, 0.005690815269578844, 0.014374362061054084, 0.0228411455985031, 0.03115780628759086, 0.03946038929664473, 0.047163278837346695, 0.05498237458280129, 0.06270559732229665, 0.07083405206976819, 0.07896111101513902, 0.08766184680347634, 0.09718168504386937, 0.10784451063420147, 0.12046983354224972, 0.138524736226006, 0.28486487478573513
#], dtype='float')

#### 161213, 8 var + ht, ll/lc vs. bb, bc, bl, cc
# 40 bins
#binning = np.asarray([-0.4362980410899681, -0.3029901887013, -0.2760197837538261, -0.2520451631499839, -0.2240350719225723, -0.19436554060418346, -0.16673879845368686, -0.13721721963996075, -0.1065743796402844, -0.08160685782699525, -0.06425666851281095, -0.05067513208782195, -0.039631420242457555, -0.030189187397400775, -0.022030459751940384, -0.014436135472595838, -0.007141454346335565, -0.00014324759679893231, 0.006525467165930775, 0.013294201155865973, 0.019961856693033613, 0.02651915511708232, 0.032913017165298174, 0.03921122540192774, 0.04538034971960916, 0.05131318740113471, 0.05735888595876785, 0.06338519097312478, 0.06944200836918284, 0.07559709065154084, 0.08131872595661946, 0.08749642457776874, 0.0936785617380301, 0.10007418403866533, 0.10689697751436553, 0.11414977258860907, 0.12231465987827868, 0.1316746154425863, 0.1436350675176427, 0.16158506028893185, 0.3009639787163516],
#        dtype="float")

### 161213, 8 var + ht, ll vs. rest
# 50 bins
#binning = np.asarray([-0.4261654856777286, -0.3062779961512552, -0.28295465373610357, -0.2596877252197837, -0.23355397330780836, -0.2059041984511851, -0.17815123955515075, -0.15342741040951044, -0.13116727598087985, -0.1093210170390162, -0.08939213832133107, -0.07371482037694883, -0.06201877808426038, -0.05246219473148642, -0.044319575635604694, -0.03738399957464131, -0.031155838585039057, -0.025377174494381517, -0.02015051508571649, -0.015123248013535432, -0.010438979342334783, -0.0057266780551628125, -0.00115409535361686, 0.003230429269502415, 0.007665439978306588, 0.012139028594075918, 0.01677159683390632, 0.02133528419061496, 0.02583132928739224, 0.030436576258792293, 0.03503545128707422, 0.0398431796239319, 0.04456820277962608, 0.04914634020445271, 0.0538291512476819, 0.05850378251822719, 0.0631083231678108, 0.06770544137583533, 0.07243510529267157, 0.07718498220750417, 0.0820978755413049, 0.08735665058520604, 0.09301962890025056, 0.09863004196463988, 0.10503187166273649, 0.1120210021853552, 0.12008956041170087, 0.1297280850044895, 0.14234822019561214, 0.16153496425902286, 0.37774715118860025],
#        dtype="float")

### 161213, 7 var + ht, bb vs. rest
# 50 bins
#binning = np.asarray([-0.44429565896274786, -0.2953686301515701, -0.2724409405520482, -0.2575403351931172, -0.2456781525323163, -0.2340011833665228, -0.22225829491297303, -0.21007711331197068, -0.1966938382099644, -0.18103013114479863, -0.1631786658432569, -0.14451180019652415, -0.12672607574475522, -0.11166164106451054, -0.09873171739562578, -0.08775682464697541, -0.07818318062615419, -0.06945213162060945, -0.061159258051057035, -0.053500532594703935, -0.04602421589365229, -0.03901019535255912, -0.0322770116414474, -0.0253103517604061, -0.01860803470857079, -0.011786395801653153, -0.005268479282695608, 0.0011738234925630852, 0.007620643362176004, 0.014024106356469524, 0.020066642402092126, 0.02592427305859876, 0.03170592501761837, 0.037322445110235775, 0.042811655843039635, 0.048053262125836584, 0.053218707590653495, 0.05831354772968393, 0.06393298217106644, 0.06919837589294084, 0.07318873555863745, 0.07873895226515541, 0.08461689568895564, 0.0907417848617272, 0.0972670272772399, 0.1045349318751832, 0.11223863198404029, 0.12125279754153079, 0.13246301661742269, 0.14875433119495723, 0.29673853807688994],
#        dtype='float')

### 161214, 7 var + (real) ht, bb && cc vs. rest
# 40 bins
#binning = np.asarray([-0.40954479452557035, -0.25051508462792377, -0.21625718832826327, -0.18867004663829703, -0.16727952346072245, -0.15011927167686684, -0.13542940509963644, -0.12153119286250995, -0.10871901520430505, -0.09658581490507481, -0.08527131374249516, -0.07480031267546762, -0.06556137875889205, -0.05751665997527719, -0.051040508170322775, -0.0438071281845975, -0.03663449203461206, -0.029679462749033558, -0.02299296611542255, -0.016322028805736893, -0.00993707770962872, -0.0037175239253942676, 0.00251468509904911, 0.008725831244654314, 0.014824591957535814, 0.020968921465439955, 0.027195567697345192, 0.03337866730869944, 0.039617347215463325, 0.0459564135073927, 0.05227146789733859, 0.05826295676949662, 0.06525365084862145, 0.07320211585648417, 0.08177876705496816, 0.09164224336667169, 0.10375114907268507, 0.12048964549072434, 0.14239761636957857, 0.1786450276004902, 0.4079653718644938],
#        dtype='float')
# 40 bins, correct
binning = np.asarray([-0.40954479452557035, -0.24847710705731826, -0.21329934865206426, -0.18480170877968272, -0.1635905331194211, -0.14652682138454118, -0.13148361138475637, -0.11753560020151571, -0.10484227668242477, -0.09250040655681806, -0.08131979829275157, -0.0711924221626182, -0.0622657240016803, -0.055555926343562, -0.047974507595814606, -0.040661960867991384, -0.033525463008339834, -0.026577200584067918, -0.0200225171565405, -0.013623410849484402, -0.007351628182188456, -0.0010239301304914665, 0.005148124371497017, 0.011235351285424439, 0.017430908676610787, 0.02354917804844697, 0.029842589029353158, 0.03613097115548405, 0.04234480226133989, 0.04848603540249552, 0.05443264598377303, 0.061312488261896565, 0.0686761787816751, 0.07673041772134984, 0.08511865466913704, 0.09502856334913762, 0.10737686752077515, 0.12394213955540974, 0.14493497935609798, 0.18054171404272779, 0.4079653718644938],
        dtype='float')

n_bins = len(binning) - 1

flavors = ["b", "c", "l"]

efficiencies = {}

for flav1 in flavors:
    for flav2 in flavors:
        name = "%s%s_frac" % (flav1, flav2)

        frac = ROOT.TEfficiency(name, name, n_bins, binning)
        frac.SetStatisticOption(ROOT.TEfficiency.kMidP)
        frac.SetUseWeightedEvents()
        # Set global weight for sample
        frac.SetWeight(cross_section / event_wgt_sum)

        key = (flav1, flav2)
        efficiencies[key] = frac

chain = ROOT.TChain('t')
for f in files:
    chain.Add(f)

ROOT.TH1.SetDefaultSumw2(True)

chain.SetBranchStatus("*", 0)

chain.SetBranchStatus("hh_jets*", 1)
chain.SetBranchStatus("hh_leptons*", 1)
chain.SetBranchStatus("hh_llmetjj_HWWleptons_nobtag_csv*", 1)
chain.SetBranchStatus("event_weight", 1)
chain.SetBranchStatus("event_pu_weight", 1)
chain.SetBranchStatus("nJetsL", 1)

bdt_tmva_variables = [
    ( "lep1_p4.Pt()", "lep1_pt" ),
    ( "lep2_p4.Pt()", "lep2_pt" ),
    ( "jet1_p4.Pt()", "jet1_pt" ),
    ( "jet2_p4.Pt()", "jet2_pt" ),
    ( "jj_p4.Pt()", "jj_pt" ),
    ( "ll_p4.Pt()", "ll_pt" ),
    ( "DR_l_l", "ll_DR_l_l" ),
    #( "DR_j_j", "jj_DR_j_j" ),
    ( "ht", "ht" ),
    ( "nJetsL", "nJetsL" ),
]
#bdt_label = "2016_12_12_BDTDY_incl_vs_bb_8var"
#bdt_label = "2016_12_13_BDTDY_ll_cl_vs_bx_cc_8var_ht"
#bdt_label = "2016_12_13_BDTDY_ll_vs_rest_8var_ht"
#bdt_label = "2016_12_13_BDTDY_bb_vs_rest_7var_ht"
bdt_label = "2016_12_14_BDTDY_bb_cc_vs_rest_7var_ht_nJets"
bdt_xml_file = "/home/fynu/swertz/scratch/CMSSW_8_0_19/src/cp3_llbb/HHTools/mvaTraining_hh/weights/{}_kBDT.weights.xml".format(bdt_label)

dict_tmva_variables = { var[1]: array('f', [0]) for var in bdt_tmva_variables }
m_reader = ROOT.TMVA.Reader("Silent=1")
for var in bdt_tmva_variables:
    m_reader.AddVariable(var[1], dict_tmva_variables[var[1]])
m_reader.BookMVA(bdt_label, bdt_xml_file)

print("Loading chain...")
if not entries:
    entries = chain.GetEntries()
print("Done.")

print("Computing jet flavor fraction using %d events." % entries)

for i in range(0, entries):
    chain.GetEntry(i)

    if (i % 100 == 0):
        print("Event %d over %d" % (i + 1, entries))

    hh_jets = chain.hh_jets
    hh_leptons = chain.hh_leptons
    hh_llmetjj_HWWleptons_nobtag_csv = chain.hh_llmetjj_HWWleptons_nobtag_csv[0]

    if (hh_llmetjj_HWWleptons_nobtag_csv.ll_p4.M() <= 12):
        continue

    weight = chain.event_weight * chain.event_pu_weight * hh_llmetjj_HWWleptons_nobtag_csv.trigger_efficiency

    def pass_flavor_cut(flav1, flav2):
        return getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv.ijet1], 'gen_%s' % flav1) and getattr(hh_jets[hh_llmetjj_HWWleptons_nobtag_csv.ijet2], 'gen_%s' % flav2)

    def get_ht():
        ht = 0
        for jet in hh_jets:
            ht += jet.p4.Pt()
        for lep in hh_leptons:
            ht += lep.p4.pt()
        return ht

    def get_value(object, val):
        if not '()' in val:
            return getattr(object, val)
        else:
            # If 'val' contains an object method, we have to extract the actual method:
            method = val.split(".")[-1].strip("()")
            new_object = getattr(object, ".".join(val.split(".")[:-1]))
            return getattr(new_object, method)()

    for var in bdt_tmva_variables:
        if var[0] == "ht":
            dict_tmva_variables["ht"][0] = get_ht()
        elif var[0] == "nJetsL":
            dict_tmva_variables["nJetsL"][0] = chain.hh_nJetsL
        else:
            dict_tmva_variables[var[1]][0] = get_value(hh_llmetjj_HWWleptons_nobtag_csv, var[0])

    bdt_value = m_reader.EvaluateMVA(bdt_label)

    for flav1 in flavors:
        for flav2 in flavors:
            key = (flav1, flav2)
            efficiencies[key].FillWeighted(pass_flavor_cut(flav1, flav2), weight, bdt_value)

print("Done")
output = ROOT.TFile.Open(output, "recreate")

for key, value in efficiencies.items():
    value.Write()

output.Close()
