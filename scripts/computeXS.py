#!/usr/bin/env python

import json
import ROOT

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

## Tool to compute the cross sections for the different benchmarks
## Usage: './computeXS.py' ^^
## Expexts to find files 'benchmarks.json' and 'coefficients.json' to get the right coefficients

formula = "({1})*({Kt})^4 + ({2})*({c2})^2 + (({3})*({Kt})^2 + ({4})*({cg})^2)*({Kl})^2 + ({5})*({c2g})^2 + (({6})*({c2}) + ({7})*({Kt})*({Kl}))*({Kt})^2 + (({8})*({Kt})*({Kl}) + ({9})*({cg})*({Kl}))*({c2}) + ({10})*({c2})*({c2g}) + (({11})*({cg})*({Kl}) + ({12})*({c2g}))*({Kt})^2 + (({13})*({Kl})*({cg}) + ({14})*({c2g}))*({Kt})*({Kl}) + ({15})*({cg})*({c2g})*({Kl})"

with open("benchmarks.json") as bm_file:
    bm = json.load(bm_file)
with open("coefficients.json") as coef_file:
    coef = json.load(coef_file)
    
# NNLO for 125 GeV, in fb
# From https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGHH#Current_recommendations_for_di_H
xs_sm = 33.45

# For 125 GeV, bbWW(llnunu)
# From https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
br = 2 * 0.5824 * 0.01055 

energy = "13TeV"

coef_set = coef[energy]
coef_set.insert(0, 0)

results = {}
results_br = {}

for coupl_set in bm.items():
    m_formula = formula.format(*coef_set, **coupl_set[1])
    m_tf = ROOT.TFormula("formula", m_formula)
    ratio = m_tf.Eval(0)
    results[coupl_set[0]] = ratio*xs_sm
    results_br[coupl_set[0]] = ratio*xs_sm*br

print "JSON total XS:"
print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

print "JSON XS*BR:"
print json.dumps(results_br, sort_keys=True, indent=4, separators=(',', ': '))


