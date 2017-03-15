configuration:
  include: ['centralConfig.yml']

files:
  include: {files}

plots:
  include: ['allPlots.yml']

groups:
  include: ['groups.yml']

legend:
  {legend}

systematics:
  - lumi: 1.025
  - pu
  - elreco
  - elidiso
  - mutracking
  - muiso
  - muid
  - jjbtag
  - jec
  - jer 
  - trigeff
  - scaleUncorr
  - pdf
  - dyStat
  - dyScaleUncorr
  - dyNorm: {{type: const, value: 1.05, on: 'dyEstimation'}}
  - hdamp
  #- pdfqq
  #- pdfgg
  #- pdfqg
