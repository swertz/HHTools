#! /usr/bin/env python

import os
import yaml
import glob

#usage: python listHisto.py [yields]
from ROOT import TFile
import argparse

parser = argparse.ArgumentParser(description='Facility to produce the yml with plots information.')
parser.add_argument('--yields', help='If you just want to produce the yields and systematics.', action="store_true")
parser.add_argument('-d', '--directory', dest='directory', required=True, help='Directory of the input rootfiles.')
parser.add_argument('--blinded', dest='unblinded', help='If you want to produce blinded plots', action="store_false")
args = parser.parse_args()

if not os.path.exists(args.directory):
    parser.error("%r does not exists" % args.directory)

rootDir = args.directory
condorDir = os.path.join(rootDir, "condor/output")

# Find a ROOT file in condor output directory
root_files = glob.glob(os.path.join(condorDir, "*.root"))
if len(root_files) == 0:
    raise Exception("No ROOT files found in %r" % condorDir)

fileName = root_files[0]

print("Listing histograms found in %r" % fileName)

skim = False

file = TFile.Open(fileName) 
keys = file.GetListOfKeys() 
alreadyIn = []

# Create 'centralConfig.yml'
with open('centralConfig.yml.tpl') as tpl_handle:
    tpl = tpl_handle.read()
    tpl = tpl.format(root=condorDir)
    with open('centralConfig.yml', 'w') as f:
        f.write(tpl)

# Dictionary containing all the plots
plots = {}

logY = 'both'
if args.yields:
    logY = False
defaultStyle = {
        'log-y': logY,
        'save-extensions': ['pdf', 'png'],
        'legend-columns': 2,
        'show-ratio': True,
        'show-overflow': True,
        'show-errors': True
        }

defaultStyle_events_per_gev = defaultStyle.copy()
defaultStyle_events_per_gev.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f GeV',
        })

defaultStyle_events = defaultStyle.copy()
defaultStyle_events.update({
        'y-axis': 'Events',
        'y-axis-format': '%1% / %2$.2f',
        })

nHistos = 0

for key in keys:
    if key.GetName() not in alreadyIn and not "__" in key.GetName():

        # Keep only histograms
        if not key.ReadObj().InheritsFrom("TH1"):
            continue

        ## Some manual choices which plots to skip...
        
        #if "btagM" in key.GetName() and "blind" not in key.GetName() and "ll_M" not in key.GetName() and not args.unblinded:
        #    continue
        #if "btagM" in key.GetName() and "blind" in key.GetName() and "MVA" not in key.GetName():
        #    continue

        # skip 2D histos
        if "_vs_" in key.GetName() and "flat" not in key.GetName(): continue

        #if "highBDT" in key.GetName(): continue
        #if "highBDT" not in key.GetName(): continue
        #if "_vs_" not in key.GetName(): continue
        #if "3x25" not in key.GetName(): continue

        #if "ll_M" not in key.GetName() or "All" in key.GetName(): continue
        #if "ll_M" in key.GetName() and "All" not in key.GetName(): continue

        # if "BDT" not in key.GetName(): continue

        if not 'All' in key.GetName():
            continue

        if 'mll_cut' not in key.GetName():
            continue

        if 'inverted_mll_cut' in key.GetName():
            continue

        if 'high_mll_cut' in key.GetName():
            continue

        ## Update all the plots with title, ...

        alreadyIn.append(key.GetName())
        plot = {
                'x-axis': key.GetName(),
                'normalized': True,
                'rename': [
                    {'from': 'mll_cut', 'to': 'DY_comparison'}
                    ]
                }
        plot['labels'] = []

        if "lep1_pt" in key.GetName():
            plot['x-axis'] = "Leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep2_pt" in key.GetName():
            plot['x-axis'] = "Sub-leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet1_pt" in key.GetName():
            plot['x-axis'] = "Leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet2_pt" in key.GetName():
            plot['x-axis'] = "Sub-leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep1_eta" in key.GetName():
            plot['x-axis'] = "Leading lepton #eta"
            plot.update(defaultStyle_events)
        elif "lep2_eta" in key.GetName():
            plot['x-axis'] = "Sub-leading lepton #eta"
            plot.update(defaultStyle_events)
        elif "jet1_eta" in key.GetName():
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet2_eta" in key.GetName():
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep1_phi" in key.GetName():
            plot['x-axis'] = "Leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "lep2_phi" in key.GetName():
            plot['x-axis'] = "Sub-leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "jet1_phi" in key.GetName():
            plot['x-axis'] = "Leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet2_phi" in key.GetName():
            plot['x-axis'] = "Sub-leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet1_CSV" in key.GetName():
            plot['x-axis'] = "Leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_CSV" in key.GetName():
            plot['x-axis'] = "Sub-leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_JP" in key.GetName():
            plot['x-axis'] = "Leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_JP" in key.GetName():
            plot['x-axis'] = "Sub-leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "ll_pt_" in key.GetName():
            plot['x-axis'] = "Dilepton system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jj_pt_" in key.GetName():
            plot['x-axis'] = "Dijet system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_pt" in key.GetName():
            plot['x-axis'] = "#slash{E}_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_phi" in key.GetName():
            plot['x-axis'] = "#phi_{#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l_All_hh_llmetjj_HWWleptons_btagM_csv_cleaning_cut" in key.GetName():
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l" in key.GetName():
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DR_j_j" in key.GetName():
            plot['x-axis'] = "#DeltaR(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "ll_DPhi_l_l" in key.GetName():
            plot['x-axis'] = "#Delta#phi(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DPhi_j_j" in key.GetName():
            plot['x-axis'] = "#Delta#phi(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "llmetjj_pt_" in key.GetName():
            plot['x-axis'] = "p_{T}^{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_ll_met_" in key.GetName():
            plot['x-axis'] = "#Delta#phi(ll, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj" in key.GetName():
            plot['x-axis'] = "#Delta#phi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "minDPhi_l_met_" in key.GetName():
            plot['x-axis'] = "min(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "maxDPhi_l_met_" in key.GetName():
            plot['x-axis'] = "max(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "MT_" in key.GetName():
            plot['x-axis'] = "m_{ll#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "MTformula_" in key.GetName():
            plot['x-axis'] = "MT"
            plot.update(defaultStyle_events_per_gev)
        elif "projMET_" in key.GetName():
            plot['x-axis'] = "Projected #slash{E}_{T}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_jj_met" in key.GetName():
            plot['x-axis'] = "#Delta#phi(jj, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDPhi_j_met" in key.GetName():
            plot['x-axis'] = "min#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "maxDPhi_j_met" in key.GetName():
            plot['x-axis'] = "max#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDR_l_j" in key.GetName():
            plot['x-axis'] = "min#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "maxDR_l_j" in key.GetName():
            plot['x-axis'] = "max#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "DR_ll_jj_" in key.GetName():
            plot['x-axis'] = "#DeltaR(ll, jj)"
            plot.update(defaultStyle_events)
        elif "DR_llmet_jj" in key.GetName():
            plot['x-axis'] = "#DeltaR(ll#slash{E}_{T}, jj)"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj_" in key.GetName():
            plot['x-axis'] = "#DeltaPhi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "nllmetjj_" in key.GetName():
            plot['x-axis'] = "#llmetjj"
            plot.update(defaultStyle_events)
        elif "nLep_" in key.GetName():
            plot['x-axis'] = "Number of leptons"
            plot.update(defaultStyle_events)
        elif "nJet_" in key.GetName():
            plot['x-axis'] = "Number of jets"
            plot.update(defaultStyle_events)
        elif "nBJetMediumCSV_" in key.GetName():
            plot['x-axis'] = "Number of b-tagged jets (CSVv2 medium)"
            plot.update(defaultStyle_events)
        elif "cosThetaStar" in key.GetName():
            plot['x-axis'] = "cos(#theta^{*}_{CS})_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        
        # Here be dragons

        elif "MT2" in key.GetName():
            plot['x-axis'] = "MT2"
            plot.update(defaultStyle_events)
            if not args.unblinded:
                plot['blinded-range'] = [150, 500]

        elif "llmetjj_M_" in key.GetName():
            plot['x-axis'] = "m_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
            if not args.unblinded:
                plot['blinded-range'] = [500, 1500]

        elif "ll_M_" in key.GetName():
            plot['x-axis'] = "m_{ll} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            if "mll_cut" in key.GetName():
                plot['x-axis-range'] = [10, 76]
                if "btagM" in key.GetName(): #### Do the yields here
                    plot['for-yields'] = True
                    plot['yields-title'] = "llbb, mll cut"
        
        elif "jj_M_" in key.GetName() and "_vs_" not in key.GetName():
            plot['x-axis'] = "m_{jj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            if not args.unblinded and "no_cut" not in key.GetName():
                plot['blinded-range'] = [75, 140]

        elif "MVA_" in key.GetName() and "_vs_" not in key.GetName():
            plot['x-axis'] = "BDT output"
            plot.update(defaultStyle_events)
            if not args.unblinded and "blind" not in key.GetName():
                plot['blinded-range'] = [0, 0.6]
        
        elif "MVA_" in key.GetName() and "_vs_" in key.GetName():
            plot['x-axis'] = "BDT output, m_{jj} bins"
            plot.update(defaultStyle_events)
            
            if "3x25" in key.GetName() and "BDT_2" in key.GetName():
                plot['vertical-lines'] = [ 
                        { "line-color": 1, "line-type": 2, "line-width": 2, "value": 0.6 }, 
                        { "line-color": 1, "line-type": 2, "line-width": 2, "value": 1.7 }
                    ]
                #plot['y-axis-range'] = [0.01, 450]
                if not args.unblinded and "blind" not in key.GetName():
                    plot['blinded-range'] = [1.128, 1.7]
        
            if "3x25" in key.GetName() and "BDT_SM" in key.GetName():
                plot['vertical-lines'] = [ 
                        { "line-color": 1, "line-type": 2, "line-width": 2, "value": 0.5 }, 
                        { "line-color": 1, "line-type": 2, "line-width": 2, "value": 1.5 }
                    ]
                #plot['y-axis-range'] = [0.01, 400]
                if not args.unblinded and "blind" not in key.GetName():
                    plot['blinded-range'] = [1, 1.5]

            if "3x25" in key.GetName():
                plot['labels'] += [
                        { "size": 18, "position": [ 0.23, 0.65 ], "text": "m_{jj} < 75 GeV" },
                        { "size": 18, "position": [ 0.475, 0.735 ], "text": "75 GeV #leq m_{jj} < 140 GeV" },
                        { "size": 18, "position": [ 0.75, 0.82 ], "text": "m_{jj} #geq 140 GeV" },
                    ]

        # Default:
        
        else:
            plot.update(defaultStyle_events)

        # Further labels, style, ...

        if "gen_" in key.GetName():
            flavour = key.GetName().split("_")[1]
            plot['x-axis'] = "is "+flavour
            plot['no-data'] = True
            plot.update(defaultStyle_events)
        if any(x in key.GetName() for x in ['sr_400_ext', 'sr_650_ext']) and not args.unblinded:
            plot['no-data'] = True
        if "scaleFactor" in key.GetName():
            plot['x-axis'] = "Scale factor"
            plot.update(defaultStyle_events)
            plot['no-data'] = True

        label_x = 0.22
        label_y = 0.895
        if "MuMu" in key.GetName():
            plot['labels'] += [{
                'text': '#mu#mu channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "MuEl" in key.GetName():
            plot['labels'] += [{
                'text': '#mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "ElEl" in key.GetName():
            plot['labels'] += [{
                'text': 'ee channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif "All" in key.GetName() and "3x25" not in key.GetName():
            plot['labels'] += [{
                'text': '#mu#mu + ee + #mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        # For the 3-bin "flattened" ones
        elif "All" in key.GetName() and "3x25" in key.GetName():
            plot['labels'] += [{
                'text': '#mu#mu + ee + #mue + e#mu channels',
                'position': [0.6, label_y],
                'size': 24
                }]
            plot['legend-position'] = [0.22, 0.61, 0.62, 0.89]

        # Finally, save what we have
        plots[key.GetName()] = plot
        nHistos += 1

with open("allPlots.yml", "w") as f:
    yaml.dump(plots, f)

print "Saved configuration for {} plots in {}".format(nHistos, "allPlots.yml")
