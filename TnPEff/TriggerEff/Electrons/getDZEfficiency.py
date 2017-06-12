#! /bin/env python

from __future__ import division

import argparse
import ROOT as rt

parser = argparse.ArgumentParser(description='tnp EGM fitter')
parser.add_argument('settings'     , default = None       , help = 'setting file [mandatory]')

args = parser.parse_args()

print '===> settings %s <===' % args.settings
importSetting = 'import %s as tnpConf' % args.settings.replace('/','.').split('.py')[0]
print importSetting
exec(importSetting)

sample = tnpConf.samplesDef['data']
setattr(sample, 'tree'     ,'%s/fitter_tree' % tnpConf.tnpTreeDir )

tree = rt.TChain(sample.tree)
for p in sample.path:
    print ' adding rootfile: ', p
    tree.Add(p)

nTot = tree.GetEntries("passingMedium80X == 1 && pass_Ele23Ele12NonDZ")
nPass = tree.GetEntries("passingMedium80X == 1 && pass_Ele23Ele12NonDZ && pass_Ele23Ele12DZ")

e = nPass / nTot
error_up = rt.TEfficiency.Bayesian(nTot, nPass, 0.682689492137, 1, 1, True) - e
error_down = e - rt.TEfficiency.Bayesian(nTot, nPass, 0.682689492137, 1, 1, True)

print("DZ filter efficiency: {:.4f} + {:.4f} - {:.4f}".format(e, error_up, error_down))
