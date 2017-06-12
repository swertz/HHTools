import FWCore.ParameterSet.Config as cms

process = cms.Process("TagProbe")
process.load('FWCore.MessageService.MessageLogger_cfi')
process.source = cms.Source("EmptySource")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

mass_ = "mass"

ProbeTightIDIso = cms.PSet(
        Tight2012 = cms.vstring("pass"),
        combRelIsoPF04dBeta = cms.vdouble(0, 0.15),
        # tag_IsoMu22 = cms.vstring("pass"),
        pair_deltaR = cms.vdouble(0.3, 99999),
        dzPV = cms.vdouble(-0.5, 0.5)
        )

InputFileNames = cms.vstring(
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016B_GoldenJSON_Run276098to276384_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016C_GoldenJSON_Run276098to276384_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016D_GoldenJSON_Run276098to276384_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016E_GoldenJSON_Run276098to276384_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016F_GoldenJSON_Run276098to276384_skim.root',
        # Run G+H
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016G_GoldenJSON_Run278819to280384_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016H_v2_GoldenJSON_Run281613to284035_skim.root',
        'file:/home/fynu/sbrochet/storage/TnP/Muons/Run2016/tag_IsoMu24/TnPTree_80XRereco_Run2016H_GoldenJSON_Run284036to284044_skim.root'
        )

process.TriggerEfficiencies = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
        NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),

        Variables = cms.PSet(
            eta  = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            abseta  = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pt   = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            mass = cms.vstring("Tag-muon Mass", "70", "130", "GeV/c^{2}"),
            dzPV = cms.vstring("dzPV", "-1000", "1000", ""),
            combRelIsoPF04dBeta = cms.vstring("dBeta rel iso dR 0.4", "-2", "9999999", ""),
            pair_deltaR = cms.vstring("dR between tag and probe", "0", "9999999", ""),

            l1pt = cms.vstring("L1 pt", "0", "1000", "GeV/c"),
            l1q = cms.vstring("L1 quality", "0", "50", ""),
            l2pt = cms.vstring("L2 pt", "0", "1000", "GeV/c"),
            l3pt = cms.vstring("L3 pt", "0", "1000", "GeV/c"),
            ),

        Categories = cms.PSet(
            # PF      = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
            Tight2012 = cms.vstring("Tight Id. Muon", "dummy[pass=1,fail=0]"),
            # tag_IsoMu22 = cms.vstring("Tag pass IsoMu22", "dummy[pass=1,fail=0]"),

            DoubleIsoMu17Mu8_Mu17leg = cms.vstring("Pass DoubleMu17Mu8_Mu17 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17Mu8_Mu8leg = cms.vstring("Pass DoubleMu17Mu8_Mu8 Mu8 leg", "dummy[pass=1,fail=0]"),

            DoubleIsoMu17Mu8_IsoMu17leg = cms.vstring("Pass DoubleMu17Mu8_IsoMu17 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17Mu8_IsoMu8leg = cms.vstring("Pass DoubleMu17Mu8_Mu8 IsoMu8 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17TkMu8_TkMu8leg = cms.vstring("Pass DoubleMu17Mu8_TkMu8 TkMu8 leg", "dummy[pass=1,fail=0]"),

            Mu23_TrkIsoVVL = cms.vstring("Pass Mu23_TrkIsoVVL leg", "dummy[pass=1,fail=0]"),
            ),

        Expressions = cms.PSet(

            DoubleIsoMu17Mu8_IsoMu8legORTkMu8legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu8 leg OR Pass DoubleIsoMu17TkMu8_TkMu8 leg",
                "DoubleIsoMu17Mu8_IsoMu8leg==1 || DoubleIsoMu17TkMu8_TkMu8leg==1", "DoubleIsoMu17Mu8_IsoMu8leg", "DoubleIsoMu17TkMu8_TkMu8leg"),

            DoubleIsoMu17Mu8_IsoMu17legL1CutExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu17 leg + l1 cut",
                "DoubleIsoMu17Mu8_IsoMu17leg==1 && l1pt>11",
                "DoubleIsoMu17Mu8_IsoMu17leg", "l1pt"),

            XPathIsoMu8legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu8 leg + extra cut",
                "DoubleIsoMu17Mu8_IsoMu8leg==1 && l1q>8",
                "DoubleIsoMu17Mu8_IsoMu8leg", "l1q"),

            # XPathIsoMu17legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu17 leg + extra cut",
                # "DoubleIsoMu17Mu8_IsoMu17leg==1 && l1pt>13 && l1q>8",
                # "DoubleIsoMu17Mu8_IsoMu17leg", "l1pt", "l1q"),

            # XPathIsoMu12legExpr = cms.vstring("Pass IsoMu12 leg (= IsoMu8 + extra cuts)",
                # "DoubleIsoMu17Mu8_IsoMu8leg==1 && l1pt>5 && l1q>8 && l2pt>5 && l3pt>12",
                # "DoubleIsoMu17Mu8_IsoMu8leg", "l1pt", "l1q", "l2pt", "l3pt"),
            ),

        Cuts = cms.PSet(
            DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg", "DoubleIsoMu17Mu8_IsoMu8legORTkMu8legExpr", "0.5"),
            DoubleIsoMu17Mu8_IsoMu17legL1Cut = cms.vstring("DoubleIsoMu17Mu8_IsoMu17legL1Cut", "DoubleIsoMu17Mu8_IsoMu17legL1CutExpr", "0.5"),

            XPathIsoMu8leg = cms.vstring("XPathIsoMu8leg", "XPathIsoMu8legExpr", "0.5"),
            # XPathIsoMu17leg = cms.vstring("XPathIsoMu17leg", "XPathIsoMu17legExpr", "0.5"),
            # XPathIsoMu12leg = cms.vstring("XPathIsoMu12leg", "XPathIsoMu12legExpr", "0.5")

            ),


        PDFs = cms.PSet(
            voigtPlusExpo = cms.vstring(
                "Voigtian::signal(mass, mean[90,80,100], width[2.495], sigma[3,1,20])".replace("mass", mass_),
                "Exponential::backgroundPass(mass, lp[0,-5,5])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[0,-5,5])".replace("mass",mass_),
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusExpo = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,2,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])".replace("mass",mass_),
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})".replace("mass",mass_),
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCMS = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.02, 0.01,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                "RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.02, 0.01,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCMSbeta0p2 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.001, 0.,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                "RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.03, 0.02,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                #"RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.001, 0.01,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                #"RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.001, 0.01,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                )
            ),

    InputFileNames = InputFileNames,
    InputTreeName = cms.string("fitter_tree"),
    InputDirectoryName = cms.string("tpTree"),
    OutputFileName = cms.string("TnP_TriggerEff_data_Run2016_BCDEFGH.root"),

    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(40),
    saveDistributionsPlot = cms.bool(False),

    Efficiencies = cms.PSet(

            # Double Mu filters
            DoubleIsoMu17Mu8_IsoMu17leg_pt_eta = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu17legL1Cut", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 0.9, 1.2, 2.1, 2.4),
                    pt = cms.vdouble(0, 16, 16.5, 16.75, 17, 17.25, 17.5, 18, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg_pt_eta = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 0.9, 1.2, 2.1, 2.4),
                    pt = cms.vdouble(0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            # XPath filters
            XPathIsoMu23leg_pt_eta = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("Mu23_TrkIsoVVL", "pass"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 0.9, 1.2, 2.1, 2.4),
                    pt = cms.vdouble(0, 21, 22.5, 22.75, 23, 23.25, 23.5, 24, 25, 27, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            XPathIsoMu8leg_pt_eta = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("XPathIsoMu8leg", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 0.9, 1.2, 2.1, 2.4),
                    pt = cms.vdouble(0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            ),
    )

process.TriggerEfficienciesVsNPV = process.TriggerEfficiencies.clone(
        Efficiencies = cms.PSet(),
        OutputFileName = cms.string("TnP_TriggerEff_data_Run2016_BCDEFGH_vs_npv.root")
        )

process.TriggerEfficienciesVsNPV.Variables.tag_nVertices = cms.vstring("Number of vertices", "0", "999", "")

process.TriggerEfficienciesVsNPV.Efficiencies.XPathIsoMu23leg_npv = process.TriggerEfficiencies.Efficiencies.XPathIsoMu23leg_pt_eta.clone(
        BinnedVariables = cms.PSet(
                ProbeTightIDIso,
                pt = cms.vdouble(25, 5000),
                tag_nVertices = cms.vdouble(2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5, 22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5, 40.5, 42.5, 44.5, 46.5, 48.5, 50.5)
            )
        )

process.TriggerEfficienciesVsNPV.Efficiencies.XPathIsoMu8leg_npv = process.TriggerEfficiencies.Efficiencies.XPathIsoMu8leg_pt_eta.clone(
        BinnedVariables = cms.PSet(
                ProbeTightIDIso,
                pt = cms.vdouble(10, 5000),
                tag_nVertices = cms.vdouble(2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5, 22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5, 40.5, 42.5, 44.5, 46.5, 48.5, 50.5)
            )
        )

process.TriggerEfficienciesVsNPV.Efficiencies.DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg_npv = process.TriggerEfficiencies.Efficiencies.DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg_pt_eta.clone(
        BinnedVariables = cms.PSet(
                ProbeTightIDIso,
                pt = cms.vdouble(10, 5000),
                tag_nVertices = cms.vdouble(2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5, 22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5, 40.5, 42.5, 44.5, 46.5, 48.5, 50.5)
            )
        )

process.TriggerEfficienciesVsNPV.Efficiencies.DoubleIsoMu17TkMu8_IsoMu17leg_npv = process.TriggerEfficiencies.Efficiencies.DoubleIsoMu17Mu8_IsoMu17leg_pt_eta.clone(
        BinnedVariables = cms.PSet(
                ProbeTightIDIso,
                pt = cms.vdouble(19, 5000),
                tag_nVertices = cms.vdouble(2.5, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5, 18.5, 20.5, 22.5, 24.5, 26.5, 28.5, 30.5, 32.5, 34.5, 36.5, 38.5, 40.5, 42.5, 44.5, 46.5, 48.5, 50.5)
            )
        )

process.TriggerEfficienciesOnlyPT = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
        NumCPU = cms.uint32(1),
        SaveWorkspace = cms.bool(False),

        Variables = cms.PSet(
            eta  = cms.vstring("muon #eta", "-2.5", "2.5", ""),
            abseta  = cms.vstring("muon |#eta|", "0", "2.5", ""),
            pt   = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
            mass = cms.vstring("Tag-muon Mass", "70", "130", "GeV/c^{2}"),
            dzPV = cms.vstring("dzPV", "-1000", "1000", ""),
            combRelIsoPF04dBeta = cms.vstring("dBeta rel iso dR 0.4", "-2", "9999999", ""),
            pair_deltaR = cms.vstring("dR between tag and probe", "0", "9999999", ""),

            l1pt = cms.vstring("L1 pt", "0", "1000", "GeV/c"),
            l1q = cms.vstring("L1 quality", "0", "50", ""),
            l2pt = cms.vstring("L2 pt", "0", "1000", "GeV/c"),
            l3pt = cms.vstring("L3 pt", "0", "1000", "GeV/c"),
            ),

        Categories = cms.PSet(
            # PF      = cms.vstring("PF Muon", "dummy[pass=1,fail=0]"),
            Tight2012 = cms.vstring("Tight Id. Muon", "dummy[pass=1,fail=0]"),
            # tag_IsoMu22 = cms.vstring("Tag pass IsoMu22", "dummy[pass=1,fail=0]"),

            DoubleIsoMu17Mu8_Mu17leg = cms.vstring("Pass DoubleMu17Mu8_Mu17 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17Mu8_Mu8leg = cms.vstring("Pass DoubleMu17Mu8_Mu8 Mu8 leg", "dummy[pass=1,fail=0]"),

            DoubleIsoMu17Mu8_IsoMu17leg = cms.vstring("Pass DoubleMu17Mu8_IsoMu17 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17Mu8_IsoMu8leg = cms.vstring("Pass DoubleMu17Mu8_Mu8 IsoMu8 leg", "dummy[pass=1,fail=0]"),
            DoubleIsoMu17TkMu8_TkMu8leg = cms.vstring("Pass DoubleMu17Mu8_TkMu8 TkMu8 leg", "dummy[pass=1,fail=0]"),

            Mu23_TrkIsoVVL = cms.vstring("Pass Mu23_TrkIsoVVL leg", "dummy[pass=1,fail=0]"),
            ),

        Expressions = cms.PSet(

            DoubleIsoMu17Mu8_IsoMu8legORTkMu8legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu8 leg OR Pass DoubleIsoMu17TkMu8_TkMu8 leg",
                "DoubleIsoMu17Mu8_IsoMu8leg==1 || DoubleIsoMu17TkMu8_TkMu8leg==1", "DoubleIsoMu17Mu8_IsoMu8leg", "DoubleIsoMu17TkMu8_TkMu8leg"),

            DoubleIsoMu17Mu8_IsoMu17legL1CutExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu17 leg + l1 cut",
                "DoubleIsoMu17Mu8_IsoMu17leg==1 && l1pt>11",
                "DoubleIsoMu17Mu8_IsoMu17leg", "l1pt"),

            XPathIsoMu8legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu8 leg + extra cut",
                "DoubleIsoMu17Mu8_IsoMu8leg==1 && l1q>8",
                "DoubleIsoMu17Mu8_IsoMu8leg", "l1q"),

            # XPathIsoMu17legExpr = cms.vstring("Pass DoubleIsoMu17Mu8_IsoMu17 leg + extra cut",
                # "DoubleIsoMu17Mu8_IsoMu17leg==1 && l1pt>13 && l1q>8",
                # "DoubleIsoMu17Mu8_IsoMu17leg", "l1pt", "l1q"),

            # XPathIsoMu12legExpr = cms.vstring("Pass IsoMu12 leg (= IsoMu8 + extra cuts)",
                # "DoubleIsoMu17Mu8_IsoMu8leg==1 && l1pt>5 && l1q>8 && l2pt>5 && l3pt>12",
                # "DoubleIsoMu17Mu8_IsoMu8leg", "l1pt", "l1q", "l2pt", "l3pt"),
            ),

        Cuts = cms.PSet(
            DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg", "DoubleIsoMu17Mu8_IsoMu8legORTkMu8legExpr", "0.5"),
            DoubleIsoMu17Mu8_IsoMu17legL1Cut = cms.vstring("DoubleIsoMu17Mu8_IsoMu17legL1Cut", "DoubleIsoMu17Mu8_IsoMu17legL1CutExpr", "0.5"),

            XPathIsoMu8leg = cms.vstring("XPathIsoMu8leg", "XPathIsoMu8legExpr", "0.5"),
            # XPathIsoMu17leg = cms.vstring("XPathIsoMu17leg", "XPathIsoMu17legExpr", "0.5"),
            # XPathIsoMu12leg = cms.vstring("XPathIsoMu12leg", "XPathIsoMu12legExpr", "0.5")

            ),


        PDFs = cms.PSet(
            voigtPlusExpo = cms.vstring(
                "Voigtian::signal(mass, mean[90,80,100], width[2.495], sigma[3,1,20])".replace("mass", mass_),
                "Exponential::backgroundPass(mass, lp[0,-5,5])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[0,-5,5])".replace("mass",mass_),
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusExpo = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,2,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])".replace("mass",mass_),
                "efficiency[0.9,0,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusExpoMin70 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])".replace("mass",mass_),
                "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCheb = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                #par3
                "RooChebychev::backgroundPass(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})".replace("mass",mass_),
                "RooChebychev::backgroundFail(mass, {a0[0.25,0,0.5], a1[-0.25,-1,0.1],a2[0.,-0.25,0.25]})".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCMS = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.02, 0.01,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                "RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.02, 0.01,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                ),
            vpvPlusCMSbeta0p2 = cms.vstring(
                "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])".replace("mass",mass_),
                "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])".replace("mass",mass_),
                "RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.001, 0.,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                "RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.03, 0.02,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                #"RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.001, 0.01,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])".replace("mass",mass_),
                #"RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.001, 0.01,0.1], gammaFail[0.001, 0.,0.1], peakPass)".replace("mass",mass_),
                "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
                "efficiency[0.9,0.7,1]",
                "signalFractionInPassing[0.9]"
                )
            ),

    InputFileNames = InputFileNames,
    InputTreeName = cms.string("fitter_tree"),
    InputDirectoryName = cms.string("tpTree"),
    OutputFileName = cms.string("TnP_TriggerEff_data_Run2016_BCDEFGH_only_vs_pt.root"),

    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(40),
    saveDistributionsPlot = cms.bool(False),

    Efficiencies = cms.PSet(

            # Double Mu filters
            DoubleIsoMu17Mu8_IsoMu17leg_pt = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu17legL1Cut", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 2.4),
                    pt = cms.vdouble(0, 16, 16.5, 16.75, 17, 17.25, 17.5, 18, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg_pt = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu8legORTkMu8leg", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 2.4),
                    pt = cms.vdouble(0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            # XPath filters
            XPathIsoMu23leg_pt = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("Mu23_TrkIsoVVL", "pass"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 2.4),
                    pt = cms.vdouble(0, 21, 22.5, 22.75, 23, 23.25, 23.5, 24, 25, 27, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            # XPathIsoMu12leg_pt = cms.PSet(
                # EfficiencyCategoryAndState = cms.vstring("XPathIsoMu12leg", "above"),
                # BinnedVariables = cms.PSet(
                    # ProbeTightIDIso,

                    # abseta = cms.vdouble(0, 2.4),
                    # pt = cms.vdouble(0, 11.5, 11.75, 12, 12.25, 12.5, 13, 15, 20, 25, 30, 40, 50, 60, 80, 120, 200, 500)
                    # ),

                # UnbinnedVariables = cms.vstring('mass'),
                # BinToPDFmap = cms.vstring('vpvPlusExpo')
                # ),

            XPathIsoMu8leg_pt = cms.PSet(
                EfficiencyCategoryAndState = cms.vstring("XPathIsoMu8leg", "above"),
                BinnedVariables = cms.PSet(
                    ProbeTightIDIso,

                    abseta = cms.vdouble(0, 2.4),
                    pt = cms.vdouble(0, 7.5, 7.75, 8, 8.25, 8.5, 9, 10, 12, 15, 20, 30, 40, 50, 60, 80, 120, 200, 500)

                    ),

                UnbinnedVariables = cms.vstring('mass'),
                BinToPDFmap = cms.vstring('vpvPlusExpo')
                ),

            ),
    )

process.path = cms.Path(process.TriggerEfficiencies)
# process.path = cms.Path(process.TriggerEfficienciesOnlyPT)
# process.path = cms.Path(process.TriggerEfficienciesVsNPV)
