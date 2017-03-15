####### Warning: put most recent tags first! ###### 
analysis_tags = [
        'v5.0.1+80X_HHAnalysis_2017-03-01.v0', # fix for JER (only MC)
        'v5.0.0+80X_HHAnalysis_2017-03-01.v0', # the one prod to end them all
        #'v4.4.2+80X_HHAnalysis_2017-02-13.v2', # mini-prod with new SF and corrections
        #'v4.3.0+80X_HHAnalysis_2017-01-26.v0', # Fixed Muon triggers in data -> DoubleMuon, MuonEG
        #'v4.2.0+80X_HHAnalysis_2017-01-18.v0' # DoubleEG + Summer16 MC
        ]

samples_dict = {}

# Data
samples_dict["Data"] = [
    'DoubleEG',
    'MuonEG',
    'DoubleMuon',
    ]

# Main backgrounds:
samples_dict["Main_Training"] = [
    'ST_tW_top_5f_noFullyHadronicDecays_13TeV-powheg',
    'ST_tW_antitop_5f_noFullyHadronicDecays_13TeV-powheg',
    'TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_extended_ext0_plus_ext1', # TT incl NLO
    'TTTo2L2Nu_13TeV-powheg', # TT -> 2L 2Nu NLO
    ]

# DY NLO
samples_dict["DY_NLO"] = [
    'DYToLL_0J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1',
    'DYToLL_1J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1',
    'DYToLL_2J_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1',
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_extended_ext0_plus_ext1',
]

# DY LO
samples_dict["DY_LO"] = [
    # M-50 incl. merged
    # 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended',
    # M-50, binned HT > 100
    # 'DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 100-200 non-merged
    # 'DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    # 'DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 400-600 merged
    # 'DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    # M-5to50 incl.: forget it...
    # 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    # M-5to50, binned HT
    # 'DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 100-200 merged
    # 'DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400 non-merged
    # 'DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 400-600 non-merged
    # 'DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_extended', # 600-Inf merged
    ]

# Other backgrounds
# VV
samples_dict["VV_VVV"] = [
    #'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8', # VV(2L2Nu)

    'WWToLNuQQ_13TeV-powheg', # WW(LNuQQ)
    'WWTo2L2Nu_13TeV-powheg', # WW(2L2Nu)

    'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8', # WZ(3LNu)
    'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(L3Nu)
    'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(LNu2Q)
    'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # WZ(2L2Q)

    'ZZTo4L_13TeV_powheg_pythia8', # ZZ(4L)
    'ZZTo2L2Nu_13TeV_powheg_pythia8', # ZZ(2L2Nu)
    'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8', # ZZ(2L2Q)

    'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # WZZ
    'WWW_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    ]

# Higgs
samples_dict["Higgs"] = [
    # ggH ==> no H(ZZ)?
    'GluGluHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # H(WW(2L2Nu))
    'GluGluHToBB_M125_13TeV_powheg_pythia8', # H(BB)

    # ZH
    'GluGluZH_HToWWTo2L2Nu_ZTo2L_M125_13TeV_powheg_pythia8', # ggZ(LL)H(WW(2L2Nu))
    'HZJ_HToWW_M125_13TeV_powheg_pythia8', # ZH(WW)
    'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # ggZ(LL)H(BB)
    'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8', # Z(LL)H(BB)
    'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8', # ggZ(NuNu)H(BB)

    # VBF
    'VBFHToBB_M-125_13TeV_powheg_pythia8_weightfix', # VBFH(BB)
    'VBFHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8', # VBFH(WW(2L2Nu))

    # WH
    'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W+(LNu)H(BB)
    'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', # W-(LNu)H(BB)
    'HWplusJ_HToWW_M125_13TeV_powheg_pythia8', # W+H(WW)
    'HWminusJ_HToWW_M125_13TeV_powheg_pythia8', # W-H(WW)

    # bbH
    'bbHToBB_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(BB) ybyt
    'bbHToBB_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(BB) yb2
    #'bbHToWWTo2L2Nu_M-125_4FS_ybyt_13TeV_amcatnlo', # bbH(WW) ybyt
    #'bbHToWWTo2L2Nu_M-125_4FS_yb2_13TeV_amcatnlo', # bbH(WW) yb2
    ]

# Top
samples_dict["Top_Other"] = [
    'ST_t-channel_top_4f_inclusiveDecays_13TeV-powheg', # sT t-chan
    'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powheg', # sT t-chan
    'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo', # sT s-channel
    'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(LNu)
    'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', # TTW(QQ)
    'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(2L2Nu)
    'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8', # TTZ(QQ),
    'ttHTobb_M125_TuneCUETP8M2_13TeV_powheg_pythia8', # ttH(bb)
    'ttHToNonbb_M125_TuneCUETP8M2_13TeV_powheg_pythia8', # ttH(nonbb)
    #'TTJets_TuneCUETP8M1_amcatnloFXFX' ## TTbar aMC@NLO
    ]

# Wjets
samples_dict["WJets"] = [
    'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # JetsLNu

    # # HT binned
    # 'WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 200-400
    # 'WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 800-1200
    # 'WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 1200 - 2500
    # 'WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', # 2500 - Inf
    ]

# QCD ==> 30to50 missing
# samples_dict["QCD"] = 
   # 1661, # Pt-15to20EMEnriched
   # 1671, # Pt-20to30EMEnriched
   # 1681, # Pt-50to80EMEnriched
   # 1637, # Pt-80to120EMEnriched
   # 1632, # Pt-120to170EMEnriched
   # 1670, # Pt-170to300EMEnriched
   # 1645, # Pt-300toInfEMEnriched
   # #1719, # Pt-20toInfMuEnriched
   # ])



## Signals

# Resonant signal
samples_dict["Signal_Resonant"] = [
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M',
    'GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M'
]
samples_dict["Signal_BM_Resonant"] = [
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M-400',
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M-650',
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M-900',
]

# Non-resonant signal
samples_dict["Signal_NonResonant"] = [
    'GluGluToHHTo2B2VTo2L2Nu_node_'
]
# Number of samples used as basis for the reweighting
number_of_bases = 14

