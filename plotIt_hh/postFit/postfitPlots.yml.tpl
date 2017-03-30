#mjj_MuMu:
#  labels:
#  - position: [0.22, 0.895]
#    size: 24
#    text: '#CHANNEL#'
#  legend-columns: 2
#  save-extensions: [pdf, png]
#  show-errors: true
#  show-overflow: false
#  show-ratio: true
#  log-y: both
#  x-axis: m_{jj} (GeV)
#  y-axis: Events
#  y-axis-format: '%1% / %2$.2f GeV'
#
#ptjj_MuMu:
#  labels:
#  - position: [0.22, 0.895]
#    text: '#CHANNEL#'
#    size: 24
#  legend-columns: 2
#  save-extensions: [pdf, png]
#  show-errors: true
#  show-overflow: false
#  show-ratio: true
#  log-y: both
#  x-axis: Dijet system p_{T} (GeV)
#  y-axis: Events
#  y-axis-format: '%1% / %2$.2f GeV'

NN_#SIGNAL#_MuMu:
  labels:
  - position: [0.22, 0.895]
    text: '#CHANNEL#'
    size: 24
  legend-columns: 2
  save-extensions: [pdf, png]
  show-errors: true
  show-overflow: false
  show-ratio: true
  log-y: both
  x-axis: #LEGEND_NN#
  y-axis: Events
  y-axis-format: '%1%'

mjj_vs_NN_#SIGNAL#_MuMu:
  legend-columns: 2
  legend-position: [0.45, 0.61, 0.91, 0.89]
  log-y: both
  show-errors: true
  show-overflow: false
  show-ratio: true
  save-extensions: [pdf, png]
  x-axis: #LEGEND_2D#
  y-axis: Events
  y-axis-format: '%1%'
  labels:
      -
        position: [0.22, 0.895]
        text: '#CHANNEL#'
        size: 24
      -
        size: 18
        position: [ 0.24, 0.65 ]
        text: "m_{jj} < 75 GeV"
      -
        size: 18
        position: [ 0.45, 0.65 ]
        text: "75 GeV #leq m_{jj} < 140 GeV"
      -
        size: 18
        position: [ 0.76, 0.65 ]
        text: "m_{jj} #geq 140 GeV"
  vertical-lines:
      - 
        line-color: 1
        line-type: 2
        line-width: 2
        value: 1.00
      - 
        line-color: 1
        line-type: 2
        line-width: 2
        value: 1.88
