#!/usr/bin/env python

from scipy import interpolate
import numpy as np
import ROOT as R
from string import Template
import argparse
import os

from cp3_llbb.CommonTools import TFileWrapper

base_syst = [
        'jec',
        'jer',
        'elidiso',
        'muid',
        'muiso',
        'jjbtaglight',
        'jjbtagheavy',
        'pu',
        'trigeff',
        'pdf',
        'dyStat',
        'scaleUncorr',
        'dyScaleUncorr'
        ]
jec_sources_base = [
        'AbsoluteFlavMap',
        'AbsoluteMPFBias',
        'AbsoluteScale',
        'AbsoluteStat',
        'FlavorQCD',
        'Fragmentation',
        'PileUpDataMC',
        'PileUpPtBB',
        'PileUpPtEC1',
        'PileUpPtEC2',
        'PileUpPtHF',
        'PileUpPtRef',
        'RelativeBal',
        'RelativeFSR',
        'RelativeJEREC1',
        'RelativeJEREC2',
        'RelativeJERHF',
        'RelativePtBB',
        'RelativePtEC1',
        'RelativePtEC2',
        'RelativePtHF',
        'RelativeStatEC',
        'RelativeStatFSR',
        'RelativeStatHF',
        'SinglePionECAL',
        'SinglePionHCAL',
        'TimePtEta']
base_syst += [ 'jec' + s.lower() for s in jec_sources_base ]

systematics = []
for _s in base_syst:
    systematics.append('__' + _s + 'up')
    systematics.append('__' + _s + 'down')
systematics.append('')

flavours = ['MuMu', 'MuEl', 'ElEl']

training_masses = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900]
def get_new_masses(masses):
    return np.setdiff1d(np.concatenate([ np.arange(260, 351, 5, dtype=int), np.arange(360, 901, 10, dtype=int) ]), masses)
new_masses = get_new_masses(training_masses)


def build_splines(hists, doErrors=False):
    splines = []
    nbins = hists[0][1].GetNbinsX()

    for i in range(0, nbins + 2):
        x = [] # mass
        y = [] # bin content
        for mass, h in hists:
            x.append(mass)
            if doErrors:
                y.append(h.GetBinError(i))
            else:
                y.append(h.GetBinContent(i))

        splines.append(interpolate.Akima1DInterpolator(x, y))

    return splines


def create_hists_from_splines(splines, points, bins, name):
    new_hists = []

    for point in points:
        hist = R.TH1F(Template(name).substitute(mass=point), str(point), *bins)
        hist.SetDirectory(0)
        for i, sp in enumerate(splines):
            hist.SetBinContent(i, sp(point))
        new_hists.append(hist)

    return new_hists


def apply_error_interpolation(hists, splines):
    for hist in hists:
        mass = int(hist.GetTitle())
        for i in range(0, hist.GetNbinsX() + 2):
            hist.SetBinError(i, splines[i](mass))


def build_interpolated_hists(hists, new_masses, flav, syst):
    n_bins = hists[0][1].GetNbinsX()
    bin_range = (n_bins, hists[0][1].GetBinLowEdge(1), hists[0][1].GetBinLowEdge(n_bins))

    splines = build_splines(hists)
    new_hists = create_hists_from_splines(splines, new_masses, bin_range, hist_template.safe_substitute(flavor=flav, syst=syst))

    if syst == '':
        splines = build_splines(hists, doErrors=True)
        apply_error_interpolation(new_hists, splines)

    return new_hists


def interpolate_backgrounds(args):
    validation_hists = {}

    for _file in args.inputs:
        print('Working on {} ...'.format(_file))

        file_handle = TFileWrapper.Open(_file)
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))

        new_hists = []

        for flav in flavours:
            for syst in systematics:
                hists = []
                
                for mass in training_masses:
                    histogram_name = hist_template.substitute(mass=mass, flavor=flav, syst=syst)

                    hist = file_handle.Get(histogram_name)
                    if not hist or not hist.InheritsFrom("TH1"):
                        continue
                    hist.SetDirectory(R.nullptr)
                    hists.append((mass, hist))

                if len(hists) == 0:
                    continue
                
                interp_hists = build_interpolated_hists(hists, new_masses, flav, syst)

                if syst == '' and args.validate is not None:
                    n_bins = hists[0][1].GetNbinsX()
                    bin_range = (n_bins, hists[0][1].GetBinLowEdge(1), hists[0][1].GetBinLowEdge(n_bins))
                    validation = R.TH2F('validation_' + flav + syst, '', len(new_masses) - 1, np.array(new_masses, dtype=float), *bin_range)
                    validation.SetDirectory(0)
                    for b in range(1, n_bins + 1):
                        for m in range(len(new_masses) - 1):
                            validation.SetBinContent(m + 1, b, interp_hists[m].GetBinContent(b))
                    validation_hists.setdefault(_file.split('.root')[0], []).append(validation)

                new_hists += interp_hists

        file_handle.Close()
        
        file_handle = R.TFile.Open(_file, 'update')
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))
        for _h in new_hists:
            _h.Write()
        file_handle.Close()

    if len(validation_hists) != 0:
        file_handle = R.TFile.Open(args.validate, 'update')
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))
        for _f in validation_hists.keys():
            file_handle.cd()
            if file_handle.cd(_f) == 0:
                file_handle.mkdir(_f)
            file_handle.cd(_f)
            for _h in validation_hists[_f]:
                _h.Write("", R.TFile.kOverwrite)
        file_handle.Close()


def interpolate_signals(args):
    if args.spin == '0':
        training_masses = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 750, 800, 900]
        new_masses = get_new_masses(training_masses)
        file_template = Template('GluGluToRadionToHHTo2B2VTo2L2Nu_M-${mass}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root')
        validation_dir = 'signal_radion'

    if args.spin == '2':
        training_masses = [260, 270, 300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900]
        new_masses = get_new_masses(training_masses)
        file_template = Template('GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-${mass}_narrow_Summer16MiniAODv2_v5.0.1+80X_HHAnalysis_2017-03-01.v0_histos.root')
        validation_dir = 'signal_graviton'

    validation_hists = []
    hists = {}
    new_hists = {}
    
    for mass in training_masses:
        file_name = os.path.join(args.input, file_template.substitute(mass=mass))
        file_handle = TFileWrapper.Open(file_name)
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))
        print('Working on {} ...'.format(file_name))
        
        for flav in flavours:
            hists.setdefault(flav, {})
            for syst in systematics:
                histogram_name = hist_template.substitute(mass=mass, flavor=flav, syst=syst)
                hist = file_handle.Get(histogram_name)
                if not hist or not hist.InheritsFrom("TH1"):
                    continue
                hist.SetDirectory(R.nullptr)
                hists[flav].setdefault(syst, []).append((mass, hist))     
        
        file_handle.Close()

    for flav in flavours:
        new_hists[flav] = {}
        for syst in hists[flav].keys():
            if len(hists[flav][syst]) == 0:
                continue
                
            new_hists[flav][syst] = build_interpolated_hists(hists[flav][syst], new_masses, flav, syst)
            
            if syst == '' and args.validate is not None:
                hist = hists[flav][syst][0][1]
                n_bins = hist.GetNbinsX()
                bin_range = (n_bins, hist.GetBinLowEdge(1), hist.GetBinLowEdge(n_bins))
                validation = R.TH2F('validation_' + flav + syst, '', len(new_masses) - 1, np.array(new_masses, dtype=float), *bin_range)
                validation.SetDirectory(0)
                for b in range(1, n_bins + 1):
                    for m in range(len(new_masses) - 1):
                        validation.SetBinContent(m + 1, b, new_hists[flav][syst][m].GetBinContent(b))
                validation_hists.append(validation)

    for i, mass in enumerate(new_masses):
        file_name = os.path.join(args.input, file_template.substitute(mass=mass))
        if os.path.exists(file_name):
            print('Warning: file {} already exists. Will not overwrite it.'.format(file_name))
            continue
    
        file_handle = R.TFile.Open(file_name, 'recreate')
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))
        for flav in flavours:
            for syst in hists[flav].keys():
                new_hists[flav][syst][i].Write()
        file_handle.Close()

    if args.validate is not None:
        file_handle = R.TFile.Open(args.validate, 'update')
        if not file_handle:
            raise Exception('Could not open file {}'.format(file_name))
        if file_handle.cd(validation_dir) == 0:
            file_handle.mkdir(validation_dir)
        file_handle.cd(validation_dir)
        for _h in validation_hists:
            _h.Write("", R.TFile.kOverwrite)
        file_handle.Close()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--validate', help='Validation file (optional)')
    parser.add_argument('-t', '--template', help='Template for histogram name (keys: mass, flav, syst)', default='flatDrop_mjj_vs_NN_resonant_M${mass}_${flavor}_hh_llmetjj_HWWleptons_nobtag_cmva_mll_cut_with_nobtag_to_btagM_reweighting${syst}')
    #parser.add_argument('-t', '--template', help='Template for histogram name (keys: mass, flav, syst)', default='flatDrop_mjj_vs_NN_resonant_M${mass}_${flavor}_hh_llmetjj_HWWleptons_btagM_cmva_mll_cut${syst}')

    subparsers = parser.add_subparsers()

    parser_bkg = subparsers.add_parser('bkg', help='Interpolate shapes for backgrounds')
    parser_bkg.set_defaults(func=interpolate_backgrounds)
    parser_bkg.add_argument('-i', '--inputs', nargs='+', required=True, help='Input files for backgrounds (will be modified by adding interpolated shapes)')

    parser_sig = subparsers.add_parser('sig', help='Interpolate shapes for signals')
    parser_sig.set_defaults(func=interpolate_signals)
    parser_sig.add_argument('-i', '--input', required=True, help='Input directory for signals. New files will be created in this directory.')
    parser_sig.add_argument('-s', '--spin', choices=['0', '2'], required=True, help='Do spin-0 or spin-2 samples')

    args = parser.parse_args()
    hist_template = Template(args.template)
    args.func(args)
