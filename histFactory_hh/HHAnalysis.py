import os
import ROOT as R

#### Get all the indices and functions definitions needed to retrieve the IDs/... ####

pathCMS = os.getenv("CMSSW_BASE")
if pathCMS == "":
    raise Exception("CMS environment is not valid!")
pathTT = os.path.join(pathCMS, "src/cp3_llbb/HHAnalysis/")
pathTTdefs = os.path.join(pathTT, "plugins/Indices.cc")

R.gROOT.ProcessLine(".L " + pathTTdefs + "+")
HH =  R.HHAnalysis
