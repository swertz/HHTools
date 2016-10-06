# This file was automatically created by FeynRules =.2.4
# Mathematica version: 9.0 for Mac OS X x86 (64-bit) (January 24, 2013)
# Date: Wed 17 Feb 2016 13:51:52


from object_library import all_orders, CouplingOrder


EFT = CouplingOrder(name = 'EFT',
                    expansion_order = 1,
                    hierarchy = 1)

EFT_PHIG = CouplingOrder(name = 'EFT_PHIG',
                    expansion_order = 1,
                    hierarchy = 1)

QCD = CouplingOrder(name = 'QCD',
                    expansion_order = 99,
                    hierarchy = 2,
                    perturbative_expansion = 1)

QED = CouplingOrder(name = 'QED',
                    expansion_order = 99,
                    hierarchy = 4)
