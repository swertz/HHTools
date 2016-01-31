import os,sys, inspect
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)
from basePlotter import * 
 
basePlotter = BasePlotter() 
flavour = "MuMu" # no importance, the cut will be redefined, this is just to generate the plots structure
#basePlotter.WP = ["T","T","T","T","L","L","M","M","csv"]
basePlotter.generatePlots({flavour:"dummy"}) 
plotFamilies = ["plots_lep", "plots_jet", "plots_met", "plots_ll", "plots_jj", "plots_llmetjj","plots_evt"]
plots = []
#cut = "1"
cut = "(91.1876 - ll_M) > 15 && ll_DR_l_l < 2.2 && jj_DR_j_j < 3.1 && llmetjj_DPhi_ll_jj > 1.5"
#cut = "(91.1876 - ll_M) > 15 && ll_DR_l_l < 2.2 && jj_DR_j_j < 3.1 && llmetjj_DPhi_ll_jj > 1.5 && (jj_M < 90 || jj_M > 140) "
#cut = "(91.1876 - ll_M) > 15"
# Let's get the usual plots from basePlotter
for plotFamily in plotFamilies :
    for plot in getattr(basePlotter, plotFamily) :
        plot["variable"] = plot["name"].split("_"+flavour)[0] 
        plot["name"] = plot["name"].replace("_"+flavour,"")
        plot["plot_cut"] = cut 
        plots.append(plot)
        print plot
# Now define the plots which are only there after the skimming (e.g. BDT output)
date = "2016_01_28"
spins = ["0", "2"]
masses = ["400", "650", "900"]
suffixs = ["VS_TT_DY_WoverSum_7var_noMT_bTagMM", "VS_TT_DY_WoverSum_8var_bTagMM"]#["VS_TT09_DY01_8var_bTagMM", "VS_TT1_DY0_8var_bTagMM"]
bdtTemplate = "MVA_DATE_BDT_XSPIN_MASS_SUFFIX"
afterSkim_Plots = []
for spin in spins : 
    for mass in masses : 
        for suffix in suffixs :
            afterSkim_Plots.append(
    {
        'name':  bdtTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix), 
        'variable': bdtTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix),
        'plot_cut': cut,
        'binning': '(50, -0.6, 0.6)'
    }
    )
   #         afterSkim_Plots.append(
   # {
   #     'name':  "jj_Mvs"+bdtTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix), 
   #     'variable': "jj_M:"+bdtTemplate.replace("DATE", date).replace("SPIN", spin).replace("MASS", mass).replace("SUFFIX", suffix),
   #     'plot_cut': cut,
   #     'binning': '(50, -0.6, 0.6, 50, 0, 250)',
   #     'x-axis': 'BDT output',
   #     'y-axis': 'm_{jj}'
   # }
   # )
print afterSkim_Plots
#afterSkim_Plots = [
#    {
#        'name':  'BDT_X0_400_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X0_400_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    },
#    {
#        'name':  'BDT_X0_650_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X0_650_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    },
#    {
#        'name':  'BDT_X0_900_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X0_900_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    },
#    {
#        'name':  'BDT_X2_400_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X2_400_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    },
#    {
#        'name':  'BDT_X2_650_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X2_650_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    },
#    {
#        'name':  'BDT_X2_900_vsTT_%s_lepIso_%s_lepID_%s_jetID_%s_btag_%s%s'%(basePlotter.llFlav, basePlotter.llIsoCat, basePlotter.llIDCat, basePlotter.jjIDCat, basePlotter.jjBtagCat, basePlotter.suffix),
#        'variable': "MVA_2016_01_14_BDT_X2_900_vsTT_9var_MTnoMjj_cleanCut_PTll_allFlavour",
#        'plot_cut': cut,
#        'binning': '(50, -0.6, 0.6)'
#    }
#]

for plot in afterSkim_Plots :
    plots.append(plot)
for plot in plots :
    plot["weight"] = "event_weight * ll_scaleFactor * jj_scaleFactor"
    
        
        



