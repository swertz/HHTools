#! /bin/env python

import sys, os, json
import copy
import datetime
import subprocess

import argparse

from cp3_llbb.CommonTools.condorTools import condorSubmitter

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE, 'bin', SCRAM_ARCH))
from SAMADhi import Dataset, Sample, DbStore

import inspect
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from sampleList import samples_dict, number_of_bases, analysis_tags

# Connect to the database
dbstore = DbStore()

def build_sample_name(name, tag):
    return "{}*{}".format(name, tag)

def get_sample_ids_from_name(name):
    results = dbstore.find(Sample, Sample.name.like(unicode(name.replace('*', '%'))))

    if results.count() == 0:
        return None

    if results.count() > 1:
        print("Note: more than one sample found in the database matching %r. This is maybe not what you expected:" % name)
        for sample in results:
            print("    %s" % sample.name)

    ids = []
    for sample in results:
        ids.append(sample.sample_id)

    return ids

def get_sample(iSample):
    resultset = dbstore.find(Sample, Sample.sample_id == iSample)
    return resultset.one()

# Configure number of files processed by each condor job -- NOT used
# Factor is passed as argument to script
# `sample` is DB name
def get_sample_splitting(sample, factor=2):
    nfiles = 10
    if "TTTo2L2Nu" in sample:
        nfiles = 2
    if "DYToLL_2J" in sample:
        nfiles = 4
    if "WZ" in sample or "ZZ" in sample:
        nfiles = 3
    if "DoubleMu" in sample or "DoubleEG" in sample or "MuonEG" in sample:
        nfiles = 20
    return nfiles * factor

# Configure number of events processed by each condor job
# Factor is passed as argument to script
# `sample` is DB name
def get_sample_events_per_job(sample, factor=1):
    nevents = 50000
    if "DoubleMu" in sample or "DoubleEG" in sample or "MuonEG" in sample:
        nevents = 75000
    if "node" in sample:
        nevents = 75000
    if "TTTo" in sample:
        nevents = 25000
    return nevents * factor

workflows = {}

class Configuration:
    def __init__(self, config, workflow='default', mode='plot', suffix='', samples=[], generation_args={}):
        self.samples = samples
        self.sample_ids = []
        self.configuration_file = config
        self.suffix = suffix
        self.mode = mode
        self.generation_args = generation_args

        if workflow not in workflows.keys():
            workflows[workflow] = [ self ]
        else:
            workflows[workflow].append(self)
        
        if mode == "plots":
            self.toolScript = "createPlotter.sh"
            self.executable = "plotter.exe"
            self.configPath = scriptDir
        elif mode == "skim":
            self.toolScript = "createSkimmer.sh"
            self.executable = "skimmer.exe"
            self.configPath = scriptDir
        else:
            raise Exception("Configuration mode '{}' not recognised".format(mode))
        
        self.config_file = os.path.join(self.configPath, self.configuration_file)


    def write_args_json(self):
        json_file = os.path.join("/tmp", os.getenv("USER") + "_factory.json")
        with open(json_file, 'w') as f:
            json.dump(self.generation_args, f)

    def get_sample_ids(self):
        for sample_class in self.samples:
            for sample in samples_dict[sample_class]:
                found = False
                for tag in analysis_tags:
                    ids_ = get_sample_ids_from_name(build_sample_name(sample, tag))
                    if ids_:
                        found = True
                        self.sample_ids.extend(ids_)
                        break

                if not found:
                    raise Exception("No sample found in the database for %r" % sample)

####### Different configurations for possible workflows ###### 

# Skim only DY to train the reweighting BDT
SkimDYforBDTTraining = Configuration('generateTrees.py', workflow='skim_dy_bdt', mode='skim', suffix='_for_dy', samples=['DY_NLO'], generation_args={
            'do_lljj': True,
            'do_llbb': False,
            'flavour': 'SF',
            'branches': ['basic', 'flavour', 'weights']
        })

# Skim main samples to train the NN
SkimForNNTraining_Main = Configuration('generateTrees.py', workflow='skim_nn_training', mode='skim', samples=['Main_Training'], generation_args={
            'flavour': 'All',
            'branches': ['basic', 'weights']
        })
SkimForNNTraining_ForDY = Configuration('generateTrees.py', workflow='skim_nn_training', mode='skim', suffix='_for_dy', samples=['DY_NLO'], generation_args={
            'do_lljj': True,
            'do_llbb': False,
            'flavour': 'All',
            'branches': ['basic', 'weights', 'dy_rwgt']
        })

# Plot the DY BDT in different flavour fractions before btagging, only for DY
PlotsForDYFractions = Configuration('generatePlots.py', workflow='dy_fractions', mode='plots', suffix='_for_dy', samples=['DY_NLO'], generation_args={
            'sample_type': 'MC',
            'syst': True,
            'syst_split_jec': True,
            'syst_split_pdf': True,
            'lljj_categories': ['SF'],
            'lljj_stages': ['no_cut'],
            'lljj_plots': ['dy_bdt', 'dy_bdt_flavour', 'btag_efficiencies'],
        })

# General plots
MainPlots_ForMC = Configuration('generatePlots.py', workflow='plot_main', mode='plots', samples=[
            "Main_Training",
            "DY_NLO",
            #"Higgs",
            #"VV_VVV",
            #"Top_Other",
            #"WJets",
        ], generation_args={
            'sample_type': 'MC',
            'lljj_plots': ['basic', 'dy_bdt'],
            'llbb_plots': ['basic', 'dy_bdt', 'nn'],
            'syst': True,
            'skim_MuEl_stages': True,
            'llbb_stages': ['mll_cut', 'inverted_mll_cut', 'mll_peak'],
            'lljj_stages': ['mll_cut', 'no_cut'],
        })
MainPlots_ForData = Configuration('generatePlots.py', workflow='plot_main', suffix='_for_data', mode='plots', samples=['Data'], generation_args={
            'sample_type': 'Data',
            'lljj_plots': ['basic', 'dy_bdt'],
            'llbb_plots': ['basic', 'dy_bdt', 'nn'],
            'syst': True,
            'skim_MuEl_stages': True,
            'llbb_stages': ['mll_cut', 'inverted_mll_cut', 'mll_peak'],
            'lljj_stages': ['mll_cut', 'no_cut'],
        })
MainPlots_ForSignal = Configuration('generatePlots.py', workflow='plot_main', suffix='_for_signal', mode='plots', samples=['Signal_BM_Resonant', 'Signal_NonResonant'], generation_args={
            'sample_type': 'Signal',
            'llbb_plots': ['basic', 'dy_bdt', 'nn'],
            'syst': True,
            'skim_MuEl_stages': True,
            'llbb_stages': ['mll_cut', 'inverted_mll_cut', 'mll_peak'],
        })

# Plots for 2D limits
NN2DPlots_ForMC = Configuration('generatePlots.py', workflow='plot_nn_2d', mode='plots', samples=[
            "Main_Training",
            "DY_NLO",
            #"Higgs",
            #"VV_VVV",
            #"Top_Other",
            #"WJets",
        ], generation_args={
            'sample_type': 'MC',
            'llbb_stages': ['mll_cut'],
            'llbb_plots': ['mjj_vs_nn'],
            'syst': True,
            'syst_split_jec': True,
            #'syst_split_pdf': True,
        })
NN2DPlots_ForData = Configuration('generatePlots.py', workflow='plot_nn_2d', suffix='_for_data', mode='plots', samples=['Data'], generation_args={
            'sample_type': 'Data',
            'llbb_stages': ['mll_cut'],
            'llbb_plots': ['mjj_vs_nn'],
            'syst': True,
            'syst_split_jec': True,
            #'syst_split_pdf': True,
        })
NN2DPlots_ForSignal = Configuration('generatePlots.py', workflow='plot_nn_2d', suffix='_for_signal', mode='plots', samples=['Signal_Resonant', 'Signal_NonResonant'], generation_args={
            'sample_type': 'Signal',
            'llbb_stages': ['mll_cut'],
            'llbb_plots': ['mjj_vs_nn'],
            'syst': True,
            'syst_split_jec': True,
            #'syst_split_pdf': True,
        })

# Testing area
TestPlots_ForMC = Configuration('generatePlots.py', workflow='test', mode='plots', samples=["Main_Training", "DY_NLO"], generation_args={
            'sample_type': 'MC',
            'llbb_plots': ['basic'],
            'llbb_stages': ['mll_cut', 'no_cut', 'mll_peak'],
            'llbb_categories': ['ElEl', 'MuMu'],
        })
TestPlots_ForData = Configuration('generatePlots.py', workflow='test', suffix='_for_data', mode='plots', samples=['Data'], generation_args={
            'sample_type': 'Data',
            'llbb_plots': ['basic'],
            'llbb_stages': ['mll_cut', 'no_cut', 'mll_peak'],
            'llbb_categories': ['ElEl', 'MuMu'],
        })
#TestPlots_ForSignal = Configuration('generatePlots.py', workflow='test', suffix='_for_signal', mode='plots', samples=['Signal_Resonant', 'Signal_NonResonant'], generation_args={
#            'sample_type': 'Signal',
#            'llbb_plots': ['other'],
#            'llbb_stages': ['mll_cut'],
#        })

##### Parse arguments and do actual work ####

parser = argparse.ArgumentParser(description='Facility to submit histFactory jobs on condor.')
parser.add_argument('-o', '--output', dest='output', default=str(datetime.date.today()), help='Name of the output directory.', required=True)
parser.add_argument('-s', '--submit', help='Choice to actually submit the jobs or not.', action="store_true")
parser.add_argument('-f', '--factor', dest='factor', type=int, default=1, help='Factor to multiply number of files sent to each job')
parser.add_argument('-t', '--test', help='Run on the output of HHAnalyzer not yet in the DB.', action="store_true")
parser.add_argument('-r', '--remove', help='Overwrite output directory if it already exists.', action="store_true")
parser.add_argument('--skip', help='Skip the building part.', action="store_true")
parser.add_argument('-w', '--workflow', dest='workflow', choices=workflows.keys(), help='Choose workflow, i.e. set of configurations', required=True)

args = parser.parse_args()

print("#### Will use workflow: {} ####\n".format(args.workflow))

configurations = workflows[args.workflow]

for c in configurations:
    c.get_sample_ids()

# Find first MC sample and use one file as skeleton
skeleton_file = None
for c in configurations:
    for id in c.sample_ids:
        sample = get_sample(id)
        if sample.source_dataset.datatype != "mc":
            continue

        skeleton_file = "/storage/data/cms/" + sample.files.any().lfn
        print("Using %r as skeleton" % skeleton_file)
        break

    if skeleton_file:
        break

if not skeleton_file:
    print("Warning: No MC file found in this job. Looking for data")

for c in configurations:
    for id in c.sample_ids:
        sample = get_sample(id)
        if sample.source_dataset.datatype != "data":
            continue

        skeleton_file = "/storage/data/cms/" + sample.files.any().lfn
        print("Using %r as skeleton" % skeleton_file)
        break

    if skeleton_file:
        break

if not skeleton_file:
    raise Exception("No file found in this job")

if args.test:
    jsonName = "jsonTest.json"
    jsonFile = open(jsonName)
    datasetDict = json.load(jsonFile)
    for datasetName in datasetDict.keys():
        rootFileName = datasetDict[datasetName]["files"][0]
        break

## Build factory instances -- can be skipped

if not args.skip:
    def create_factory(configuration, output):

        toolDir = "Factories"
        
        print("")
        print("Generating factory in %r using %r" % (output, configuration.config_file))
        print("")

        if args.remove and os.path.isdir(output):
            print "Are you sure you want to execute the following command ?"
            print "rm -r " + output
            print "Type enter if yes, ctrl-c if not."
            raw_input()
            os.system("rm -r " + output)
            print "Deleted %r folder" % output
        
        # Write temporary JSON file containing arguments for generateXX.py
        c.write_args_json()
        
        cmd = [os.path.join("../../", "CommonTools", toolDir, "build", configuration.toolScript)]
        if args.test:
            cmd += [rootFileName]
        else:
            cmd += [skeleton_file]
        cmd += [configuration.config_file, output]

        # Raise exception if failing
        subprocess.check_call(cmd)
        
        print("Done")

    for c in configurations:
        if len(c.sample_ids) > 0:
            create_factory(c, args.output + c.suffix)

## Write files needed to run on cluster

def create_condor(samples, output, executable):
    ## Create Condor submitter to handle job creating
    mySub = condorSubmitter(samples, "%s/build/" % output + executable, "DUMMY", output + "/", rescale=True)

    ## Create test_condor directory and subdirs
    mySub.setupCondorDirs()

    splitTT = False
    splitDY = False

    def get_node(db_name):
        split_name = db_name.split("_")
        node = None
        for i, it in enumerate(split_name):
            if it == "node":
                node = split_name[i+1]
                break
        if node is None:
            raise Exception("Could not extract node from DB name {}".format(db_name))
        return node

    def get_node_id(node):
        if node == "SM": return "-1"
        elif node == "box": return "0"
        else: return node

    training_grid = [ (kl, kt) for kl in [-20, 0.0001, 1, 2.4, 3.8, 5, 20] for kt in [0.5, 1, 1.75, 2.5] ]

    ## Modify the input samples to add sample cuts and stuff
    for sample in mySub.sampleCfg[:]:
        # TTbar final state splitting
        if splitTT and 'TT_TuneCUETP8M1_13TeV-powheg-pythia8_Fall15MiniAODv2' in sample["db_name"]:

            # Fully leptonic
            tt_fl_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            tt_fl_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_FL_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type >= 4 && hh_gen_ttbar_decay_type <= 10 && hh_gen_ttbar_decay_type != 7)"

            tt_fl_sample["json_skeleton"][tt_fl_sample["db_name"]] = newJson
            tt_fl_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_fl_sample)

            # Semi leptonic
            tt_sl_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            tt_sl_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_SL_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type == 2 || hh_gen_ttbar_decay_type == 3 || hh_gen_ttbar_decay_type == 7)"

            tt_sl_sample["json_skeleton"][tt_sl_sample["db_name"]] = newJson
            tt_sl_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_sl_sample)

            # Fully hadronic
            tt_fh_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            tt_fh_sample["db_name"] = sample["db_name"].replace("TT_Tune", "TT_FH_Tune")
            newJson["sample_cut"] = "(hh_gen_ttbar_decay_type == 1)"

            tt_fh_sample["json_skeleton"][tt_fh_sample["db_name"]] = newJson
            tt_fh_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(tt_fh_sample)

            mySub.sampleCfg.remove(sample)

        if splitDY and 'DYJetsToLL_' in sample["db_name"]:

            # Z + jj' ; j = b/c, j' = b/c
            dy_bb_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_bb_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBBOrCCToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_bb || hh_llmetjj_HWWleptons_nobtag_cmva.gen_cc)"

            dy_bb_sample["json_skeleton"][dy_bb_sample["db_name"]] = newJson
            dy_bb_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_bb_sample)

            # Z + jj' ; j = b/c, j' = l
            dy_bx_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_bx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYBXOrCXToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_bl || hh_llmetjj_HWWleptons_nobtag_cmva.gen_cl || hh_llmetjj_HWWleptons_nobtag_cmva.gen_bc)"

            dy_bx_sample["json_skeleton"][dy_bx_sample["db_name"]] = newJson
            dy_bx_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_bx_sample)

            # Z + jj' ; j = l, j' = l
            dy_xx_sample = copy.deepcopy(sample)
            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])

            dy_xx_sample["db_name"] = sample["db_name"].replace("DYJetsToLL", "DYXXToLL")
            newJson["sample_cut"] = "(hh_llmetjj_HWWleptons_nobtag_cmva.gen_ll)"

            dy_xx_sample["json_skeleton"][dy_xx_sample["db_name"]] = newJson
            dy_xx_sample["json_skeleton"].pop(sample["db_name"])
            mySub.sampleCfg.append(dy_xx_sample)

        # Merging with HT binned sample: add cut on inclusive one
        if 'DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"] or 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' in sample["db_name"]:
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        if 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' in sample["db_name"]:
            sample["json_skeleton"][sample["db_name"]]["sample_cut"] = "event_ht < 100"

        # Benchmark to training grid reweighting (ME-based)
        if "node" in sample["db_name"]:
            base = get_node(sample["db_name"])
            
            for grid_point in training_grid:
                kl = str(grid_point[0])
                kt = str(grid_point[1])
                
                weight_args = [get_node_id(base), kl, kt, number_of_bases]

                newSample = copy.deepcopy(sample)
                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
            
                point_str = "base_" + base + "_point_" + kl + "_" + kt
                point_str = point_str.replace(".", "p")
                newSample["db_name"] = sample["db_name"].replace("node_" + base, point_str)
                newJson["sample-weight"] = "training_grid"
                newJson["sample-weight-args"] = weight_args
            
                newSample["json_skeleton"][newSample["db_name"]] = newJson
                newSample["json_skeleton"].pop(sample["db_name"])
                mySub.sampleCfg.append(newSample)

            mySub.sampleCfg.remove(sample)

        ## Cluster to 1507 points reweighting (template-based)
        #if "all_nodes" in sample["db_name"]:
        #    ## For v1->v1 reweighting check:
        #    #for node in range(2, 14):
        #    #    node_str = "node_rwgt_" + str(node)
        #    #for node in range(1, 13):

        #    #    newSample = copy.deepcopy(sample)
        #    #    newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #    #
        #    #    node_str = "node_" + str(node)
        #    #    newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
        #    #    newJson["sample-weight"] = "cluster_" + node_str
        #    #
        #    #    newSample["json_skeleton"][newSample["db_name"]] = newJson
        #    #    newSample["json_skeleton"].pop(sample["db_name"])
        #    #    mySub.sampleCfg.append(newSample)
        #
        #    # 1507 points
        #    for node in range(0, 1507):
        #        # Skip dummy Xanda
        #        if node in [324, 910, 985, 990]: continue

        #        newSample = copy.deepcopy(sample)
        #        newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #
        #        node_str = "point_" + str(node)
        #        newSample["db_name"] = sample["db_name"].replace("all_nodes", node_str)
        #        newJson["sample-weight"] = node_str
        #
        #        newSample["json_skeleton"][newSample["db_name"]] = newJson
        #        newSample["json_skeleton"].pop(sample["db_name"])
        #        mySub.sampleCfg.append(newSample)

        #    mySub.sampleCfg.remove(sample)

        ## Cluster to MV reweighting (ME-based)
        #operators_MV = ["OtG", "Otphi", "O6", "OH"]
        #if "node" in sample["db_name"]:
        #    for base, base_name in enumerate(rwgt_base):
        #        for i, op1 in enumerate(operators_MV):
        #            newSample = copy.deepcopy(sample)
        #            newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #
        #            newSample["db_name"] = sample["db_name"].replace("node_" + base_name, "SM_" + op1)
        #            newJson["sample-weight"] = "base_" + base_name + "_SM_" + op1
        #
        #            newSample["json_skeleton"][newSample["db_name"]] = newJson
        #            newSample["json_skeleton"].pop(sample["db_name"])
        #
        #            mySub.sampleCfg.append(newSample)
        #
        #            for j, op2 in enumerate(operators_MV):
        #                if i < j: continue
        #
        #                newSample = copy.deepcopy(sample)
        #                newJson = copy.deepcopy(sample["json_skeleton"][sample["db_name"]])
        #
        #                newSample["db_name"] = sample["db_name"].replace("node_" + base_name, op1 + "_" + op2)
        #                newJson["sample-weight"] = "base_" + base_name + "_" + op1 + "_" + op2
        #
        #                newSample["json_skeleton"][newSample["db_name"]] = newJson
        #                newSample["json_skeleton"].pop(sample["db_name"])
        #
        #                mySub.sampleCfg.append(newSample)

    ## Write command and data files in the condor directory
    mySub.createCondorFiles()

    # Actually submit the jobs
    # It is recommended to do a dry-run first without submitting to condor
    if args.submit:
       mySub.submitOnCondor()

for c in configurations:
    if len(c.sample_ids) == 0:
        continue

    condor_samples = []
    for id in c.sample_ids:
        condor_samples.append({'ID': id, 'events_per_job': get_sample_events_per_job(get_sample(id).name, args.factor)})

    create_condor(condor_samples, args.output + c.suffix, c.executable)
