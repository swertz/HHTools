## Tree production

Follow https://twiki.cern.ch/twiki/bin/view/CMSPublic/ElectronTagAndProbe

```
cmsrel CMSSW_8_0_20
cd CMSSW_8_0_20/src
cmsenv
git cms-init
git cms-merge-topic fcouderc:tnp_egm_80X_Moriond17_v1.0
scram b -j 4
git clone -b egm_id_80X_v1  https://github.com/ikrav/RecoEgamma-ElectronIdentification.git ../external/slc6_amd64_gcc530/data/RecoEgamma/ElectronIdentification/data
git clone -b egm_id_80X_v1  https://github.com/ikrav/RecoEgamma-PhotonIdentification.git ../external/slc6_amd64_gcc530/data/RecoEgamma/PhotonIdentification/data
```

Apply `patch_for_tree_production.patch` on top of HEAD.

## Tree fitting

```
git clone  https://github.com/fcouderc/egm_tnp_analysis.git
cd egm_tnp_analysis
git checkout 9cce0ee490f7125adafd4c8aa910f23bc77990ee
```

Apply patch `patch_for_tree_fitting.patch`

Before running, check if the binning is correct in `etc/config/settings_ele.py` (lines 92-96)

Run:

```
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --createBins
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --createHists
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --doFit
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --doFit --altBkg
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --doFit --altSig
python tnpEGM_fitter.py etc/config/settings_ele.py --flag passingIsoEle23Leg --sumUp
```

For the other leg, switch `passingIsoEle23Leg` to `passingIsoEle12Leg` and check that binning in `etc/config/settings_ele.py` is correct (lines 92-96)
