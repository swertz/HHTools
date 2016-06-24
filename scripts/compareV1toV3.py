import ROOT as R
import os

## Tool to produce plots to compare "v1 reweighted" with "true v1" samples

baseV1 = "160621_reweightCheck_0"
rwgtV1 = "160621_reweightCheck_0"

baseName = "GluGluToHHTo2B2VTo2L2Nu_node_{}_13TeV-madgraph_v0.1.3+76X_HHAnalysis_2016-06-03.v0_histos.root"
rwgtName = "GluGluToHHTo2B2VTo2L2Nu_node_rwgt_{}_13TeV-madgraph_v0.1.3+76X_HHAnalysis_2016-06-03.v0_histos.root"

lumi = 2300
XS = 10000

if not os.path.exists("plots"):
    os.mkdir("plots")

R.gStyle.SetOptStat(0)

for node in range(2, 14):
    print "Working on node {}".format(node)

    base = os.path.join(baseV1, "condor", "output", baseName.format(node))
    rwgt = os.path.join(rwgtV1, "condor", "output", rwgtName.format(node))

    baseFile = R.TFile(base)
    baseKeys = set( [ k.GetName() for k in baseFile.GetListOfKeys() ] )

    rwgtFile = R.TFile(rwgt)
    rwgtKeys = set( [ k.GetName() for k in rwgtFile.GetListOfKeys() ] )

    usedKeys = list( baseKeys.intersection(rwgtKeys) )

    for key in usedKeys:
        baseTH1 = baseFile.Get(key)
        
        if not baseTH1.InheritsFrom("TH1") or baseTH1.InheritsFrom("TH2"): continue

        rwgtTH1 = rwgtFile.Get(key)

        baseTH1.Scale(lumi*XS)
        rwgtTH1.Scale(lumi*XS)

        baseTH1.SetLineWidth(2)
        rwgtTH1.SetLineWidth(2)
        rwgtTH1.SetLineColor(R.kRed)

        leg = R.TLegend(0.5, 0.7, 0.89, 0.89)
        leg.AddEntry(baseTH1, "Real V1 benchmark", "l")
        leg.AddEntry(rwgtTH1, "V1 -> V1 reweighted", "l")

        cnv = R.TCanvas("cnv_{}_{}".format(node, key), "V1->V1 reweighting: BM{}".format(node), 600, 600)
        baseTH1.SetTitle("V1->V1 reweighting: BM{}".format(node))
        baseTH1.GetXaxis().SetTitle(key.split("_All_")[0])
        baseTH1.Draw()
        rwgtTH1.Draw("same")
        leg.Draw("same")

        cnv.Print("plots/rwgt_{}_{}.png".format(node, key))

    baseFile.Close()
    rwgtFile.Close()
