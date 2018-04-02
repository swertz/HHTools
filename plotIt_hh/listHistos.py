#! /usr/bin/env python

import os
import yaml
import glob

import argparse

parser = argparse.ArgumentParser(description='Facility to produce the yml with plots information.')
parser.add_argument('--yields', help='If you just want to produce the yields and systematics.', action="store_true")
parser.add_argument('-d', '--directory', required=True, help='Directory of the input rootfiles.')
parser.add_argument('--unblinded', help='If you want to produce unblinded plots', action="store_true")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--lljj', help='Produce plots for lljj stage', action="store_true")
group.add_argument('--llbb', help='Produce plots for llbb stage', action="store_true")

args = parser.parse_args()

if not os.path.exists(args.directory):
    parser.error("%r does not exists" % args.directory)

rootDir = args.directory
slurmDir = os.path.join(rootDir, "slurm/output")

# Find a ROOT file in slurm output directory
root_files = glob.glob(os.path.join(slurmDir, "*.root"))
if len(root_files) == 0:
    raise Exception("No ROOT files found in %r" % slurmDir)

fileName = ""
for file in root_files:
    if "dy" not in os.path.basename(file).lower() and "HHTo2B2VTo2L2Nu" not in file:
        fileName = file
        break

print("Listing histograms found in %r" % fileName)

if args.unblinded:
    print("WARNING -- PRODUCING UNBLINDED PLOTS")

from ROOT import TFile
file = TFile.Open(fileName) 
keys = file.GetListOfKeys() 
alreadyIn = []

# Create 'hh_plotter_all.yml':
# Configure list of files and legend
with open('hh_plotter_all.yml.tpl') as tpl_handle:
    tpl = tpl_handle.read()
    if args.lljj:
        tpl = tpl.format(files="['MCFiles.yml', 'DY_MCFiles.yml', 'DataFiles.yml']", legend="position: [0.61, 0.61, 0.94, 0.89]")
    if args.llbb:
        tpl = tpl.format(files="['MCFiles.yml', 'DY_estFromData.yml', 'DataFiles.yml', 'SignalFiles.yml']", legend="include: ['legendPosition.yml']")
    with open('hh_plotter_all.yml', 'w') as f:
        f.write(tpl)

# Create 'centralConfig.yml':
# Configure root directory
with open('centralConfig.yml.tpl') as tpl_handle:
    tpl = tpl_handle.read()
    tpl = tpl.format(root=slurmDir)
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

defaultStyle_events_NN = defaultStyle.copy()
defaultStyle_events_NN.update({
        'y-axis': 'Events',
        'y-axis-format': '%1%',
        })

nHistos = 0

def should_be_blind(name):
    if args.unblinded:
        return False
    if "nobtag" in name:
        return False
    if not "mll_cut" in name or "inverted" in name:
        return False
    return True

def get_flavour(name):
    for flav in ["MuMu", "MuEl", "ElEl", "SF", "All"]:
        if flav in name:
            return flav

for key in keys:
    key_name = key.GetName()

    if key_name not in alreadyIn and not "__" in key_name:

        # Keep only histograms
        if not key.ReadObj().InheritsFrom("TH1"):
            continue

        ## Some manual choices which plots to skip...
        
        # skip 2D histos
        if "_vs_" in key_name and "flat" not in key_name: continue
        
        #if "All" in key_name: continue

        if args.lljj and 'btagM' in key_name: continue
        if args.llbb and 'btagM' not in key_name: continue

        #if not "no_cut" in key_name:
        #    continue

        if "nobtag_to_btagM_reweighting" in key_name: continue

        #if "NN" not in key_name and "jj_M" not in key_name: continue

        ## Update all the plots with title, ...

        alreadyIn.append(key_name)
        plot = {
                'x-axis': key_name,
                }
        plot['labels'] = []

        if "lep1_pt" in key_name:
            plot['x-axis'] = "Leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep2_pt" in key_name:
            plot['x-axis'] = "Sub-leading lepton p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet1_pt" in key_name:
            plot['x-axis'] = "Leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jet2_pt" in key_name:
            plot['x-axis'] = "Sub-leading jet p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "lep1_eta" in key_name:
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep2_eta" in key_name:
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet1_eta" in key_name:
            plot['x-axis'] = "Leading jet #eta"
            plot.update(defaultStyle_events)
        elif "jet2_eta" in key_name:
            plot['x-axis'] = "Sub-leading jet #eta"
            plot.update(defaultStyle_events)
        elif "lep1_phi" in key_name:
            plot['x-axis'] = "Leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "lep2_phi" in key_name:
            plot['x-axis'] = "Sub-leading lepton #phi"
            plot.update(defaultStyle_events)
        elif "jet1_phi" in key_name:
            plot['x-axis'] = "Leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet2_phi" in key_name:
            plot['x-axis'] = "Sub-leading jet #phi"
            plot.update(defaultStyle_events)
        elif "jet1_CSV" in key_name:
            plot['x-axis'] = "Leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_CSV" in key_name:
            plot['x-axis'] = "Sub-leading jet CSVv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_CMVAv2" in key_name:
            plot['x-axis'] = "Leading jet cMVAv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_CMVAv2" in key_name:
            plot['x-axis'] = "Sub-leading jet cMVAv2 discriminant"
            plot.update(defaultStyle_events)
        elif "jet1_JP" in key_name:
            plot['x-axis'] = "Leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "jet2_JP" in key_name:
            plot['x-axis'] = "Sub-leading jet JP discriminant"
            plot.update(defaultStyle_events)
        elif "ll_pt_" in key_name:
            plot['x-axis'] = "Dilepton system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "jj_pt_" in key_name:
            plot['x-axis'] = "Dijet system p_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_pt" in key_name:
            plot['x-axis'] = "#slash{E}_{T} (GeV)"
            plot.update(defaultStyle_events_per_gev)
        elif "met_phi" in key_name:
            plot['x-axis'] = "#phi_{#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l_All_hh_llmetjj_HWWleptons_btagM_csv_cleaning_cut" in key_name:
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "ll_DR_l_l" in key_name:
            plot['x-axis'] = "#DeltaR(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DR_j_j" in key_name:
            plot['x-axis'] = "#DeltaR(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "ll_DPhi_l_l" in key_name:
            plot['x-axis'] = "#Delta#phi(leading lepton, sub-leading lepton)"
            plot.update(defaultStyle_events)
        elif "jj_DPhi_j_j" in key_name:
            plot['x-axis'] = "#Delta#phi(leading jet, sub-leading jet)"
            plot.update(defaultStyle_events)
        elif "llmetjj_pt_" in key_name:
            plot['x-axis'] = "p_{T}^{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_ll_met_" in key_name:
            plot['x-axis'] = "#Delta#phi(ll, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj" in key_name:
            plot['x-axis'] = "#Delta#phi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "minDPhi_l_met_" in key_name:
            plot['x-axis'] = "min(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "maxDPhi_l_met_" in key_name:
            plot['x-axis'] = "max(#Delta#phi(lepton, #slash{E}_{T}))"
            plot.update(defaultStyle_events)
        elif "MT_" in key_name:
            plot['x-axis'] = "m_{ll#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
        elif "MTformula_" in key_name:
            plot['x-axis'] = "MT"
            plot.update(defaultStyle_events_per_gev)
        elif "HT" in key_name:
            plot['x-axis'] = "HT"
            plot.update(defaultStyle_events_per_gev)
        elif "projMET_" in key_name:
            plot['x-axis'] = "Projected #slash{E}_{T}"
            plot.update(defaultStyle_events_per_gev)
        elif "DPhi_jj_met" in key_name:
            plot['x-axis'] = "#Delta#phi(jj, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDPhi_j_met" in key_name:
            plot['x-axis'] = "min#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "maxDPhi_j_met" in key_name:
            plot['x-axis'] = "max#Delta#phi(j, #slash{E}_{T})"
            plot.update(defaultStyle_events)
        elif "minDR_l_j" in key_name:
            plot['x-axis'] = "min#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "maxDR_l_j" in key_name:
            plot['x-axis'] = "max#DeltaR(l, j)"
            plot.update(defaultStyle_events)
        elif "DR_ll_jj_" in key_name:
            plot['x-axis'] = "#DeltaR(ll, jj)"
            plot.update(defaultStyle_events)
        elif "DR_llmet_jj" in key_name:
            plot['x-axis'] = "#DeltaR(ll#slash{E}_{T}, jj)"
            plot.update(defaultStyle_events)
        elif "DPhi_ll_jj_" in key_name:
            plot['x-axis'] = "#DeltaPhi(ll, jj)"
            plot.update(defaultStyle_events)
        elif "nllmetjj_" in key_name:
            plot['x-axis'] = "#llmetjj"
            plot.update(defaultStyle_events)
        elif "nLep_" in key_name:
            plot['x-axis'] = "Number of leptons"
            plot.update(defaultStyle_events)
        elif "nJet_" in key_name:
            plot['x-axis'] = "Number of jets"
            plot.update(defaultStyle_events)
        elif "nBJetMediumCSV_" in key_name:
            plot['x-axis'] = "Number of b-tagged jets (CSVv2 medium)"
            plot.update(defaultStyle_events)
        elif "cosThetaStar" in key_name:
            plot['x-axis'] = "cos(#theta^{*}_{CS})_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events)
        
        elif "DY_BDT" in key_name:
            plot['x-axis'] = "DY reweighting BDT"
            plot['legend-position'] = [0.2, 0.52, 0.53, 0.80]
            plot.update(defaultStyle_events)
        
        elif "MT2" in key_name:
            plot['x-axis'] = "MT2"
            plot.update(defaultStyle_events)
            if should_be_blind(key_name):
                plot['blinded-range'] = [150, 500]

        elif "llmetjj_M_" in key_name:
            plot['x-axis'] = "m_{lljj#slash{E}_{T}}"
            plot.update(defaultStyle_events_per_gev)
            if should_be_blind(key_name):
                plot['blinded-range'] = [500, 1500]

        elif "ll_M_" in key_name:
            plot['x-axis'] = "m_{ll} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            #if "inverted_mll_cut" in key_name:
            #    plot['x-axis-range'] = [76, 252]
            #elif "mll_cut" in key_name:
            #    plot['x-axis-range'] = [12, 76]
            #elif "mll_peak" in key_name:
            #    plot['x-axis-range'] = [76, 106]
            
            #### Do the yields here
            btag_stage = ""
            if "btagM" in key_name:
                btag_stage = "llbb"
            else:
                btag_stage = "lljj"
            stage = ""
            if "inverted_mll_cut" in key_name:
                stage = ", inverted mll cut"
            elif "mll_cut" in key_name:
                stage = ", mll cut"
                plot['for-yields'] = True
            elif "mll_peak" in key_name:
                stage = ", mll peak"
            plot['yields-title'] = get_flavour(key_name) + ", " + btag_stage + stage
            if args.yields:
                plots['override'] = True
        
        elif "lljj_M_" in key_name:
            plot['x-axis'] = "m_{lljj} (GeV)"
            plot.update(defaultStyle_events_per_gev)

        elif "jj_M_" in key_name and "_vs_" not in key_name:
            plot['x-axis'] = "m_{jj} (GeV)"
            plot.update(defaultStyle_events_per_gev)
            if should_be_blind(key_name):
                plot['blinded-range'] = [75, 140]

        elif "NN_" in key_name and "_vs_" not in key_name:
            plot['x-axis'] = "NN output"
            plot['log-y'] = "both"
            plot.update(defaultStyle_events_NN)
            if should_be_blind(key_name):
                plot['blinded-range'] = [0.7, 1]

        elif "flat_mjj_vs_NN" in key_name:
            plot['x-axis'] = "NN output, m_{jj} bins"
            plot.update(defaultStyle_events_NN)
            plot['vertical-lines'] = [ 
                    { "line-color": 1, "line-type": 2, "line-width": 2, "value": 1.0 }, 
                    { "line-color": 1, "line-type": 2, "line-width": 2, "value": 2.0 }
                ]
            plot['labels'] += [
                    { "size": 18, "position": [ 0.24, 0.65 ], "text": "m_{jj} < 75 GeV" },
                    { "size": 18, "position": [ 0.45, 0.65 ], "text": "75 GeV #leq m_{jj} < 140 GeV" },
                    { "size": 18, "position": [ 0.76, 0.65 ], "text": "m_{jj} #geq 140 GeV" },
                ]
            plot['legend-position'] = [0.45, 0.61, 0.91, 0.89]
            if should_be_blind(key_name):
                plot['blinded-range'] = [1.7, 1.999]
        
        elif "flatDrop_mjj_vs_NN" in key_name:
            plot['x-axis'] = "NN output, m_{jj} bins"
            plot.update(defaultStyle_events_NN)
            plot['vertical-lines'] = [ 
                    { "line-color": 1, "line-type": 2, "line-width": 2, "value": 1.00 }, 
                    { "line-color": 1, "line-type": 2, "line-width": 2, "value": 1.88 }
                ]
            plot['labels'] += [
                    { "size": 18, "position": [ 0.24, 0.65 ], "text": "m_{jj} < 75 GeV" },
                    { "size": 18, "position": [ 0.45, 0.65 ], "text": "75 GeV #leq m_{jj} < 140 GeV" },
                    { "size": 18, "position": [ 0.76, 0.65 ], "text": "m_{jj} #geq 140 GeV" },
                ]
            plot['legend-position'] = [0.45, 0.61, 0.91, 0.89]
            if should_be_blind(key_name):
                plot['blinded-range'] = [1.58, 1.879]
        
        # Default:
        
        else:
            plot.update(defaultStyle_events)

        # Further labels, style, ...

        if "gen_" in key_name:
            flavour = key_name.split("_")[1]
            plot['x-axis'] = "is "+flavour
            plot['no-data'] = True
            plot.update(defaultStyle_events)
        if "scaleFactor" in key_name:
            plot['x-axis'] = "Scale factor"
            plot.update(defaultStyle_events)
            plot['no-data'] = True

        label_x = 0.22
        label_y = 0.895
        if get_flavour(key_name) == "MuMu":
            plot['labels'] += [{
                'text': '#mu#mu channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "MuEl":
            plot['labels'] += [{
                'text': '#mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "ElEl":
            plot['labels'] += [{
                'text': 'ee channel',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "SF":
            plot['labels'] += [{
                'text': '#mu#mu + ee channels',
                'position': [label_x, label_y],
                'size': 24
                }]
        elif get_flavour(key_name) == "All":
            plot['labels'] += [{
                'text': '#mu#mu + ee + #mue + e#mu channels',
                'position': [label_x, label_y],
                'size': 24
                }]

        # Finally, save what we have
        plots[key_name] = plot
        nHistos += 1

with open("allPlots.yml", "w") as f:
    yaml.dump(plots, f)

print "Saved configuration for {} plots in {}".format(nHistos, "allPlots.yml")
