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
  - lumi: 1.026
  - pu
  - elreco
  - elidiso
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
  - hdamp
  #- pdfqq
  #- pdfgg
  #- pdfqg
