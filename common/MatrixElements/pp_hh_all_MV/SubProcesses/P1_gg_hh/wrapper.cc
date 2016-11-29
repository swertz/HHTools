#include <map>
#include <utility>
#include <memory>
#include <vector>
#include <iostream>
#include <string>

#include "wrapper.h"

extern "C" {
extern struct {
    double MDL_MU_R__EXP__2;
    double MDL_SQRT__AS;
    double MDL_G__EXP__2;
    double MDL_G__EXP__3;
    double MDL_G__EXP__4;
    double MDL_MZ__EXP__2;
    double MDL_MZ__EXP__4;
    double MDL_SQRT__2;
    double MDL_MH__EXP__2;
    double MDL_LAMBDA__EXP__2;
    double MDL_MT__EXP__2;
    double MDL_MT__EXP__3;
    double MDL_AEW;
    double MDL_SQRT__AEW;
    double MDL_EE;
    double MDL_MW__EXP__2;
    double MDL_SW2;
    double MDL_CW;
    double MDL_SQRT__SW2;
    double MDL_SW;
    double MDL_G1;
    double MDL_GW;
    double MDL_VEV;
    double MDL_VEV__EXP__2;
    double MDL_LAM;
    double MDL_YT;
    double MDL_YTAU;
    double MDL_MUH;
    double MDL_DELTALAM;
    double MDL_YT__EXP__2;
    double MDL_DTTH;
    double MDL_DTTHH;
    double MDL_EE__EXP__2;
    double MDL_SW__EXP__2;
    double MDL_CW__EXP__2;
    double MDL_YT__EXP__3;
    double MDL_YT__EXP__4;
    double MDL_LAMBDA;
    double MDL_CTG;
    double MDL_C6;
    double MDL_CH;
    double MDL_CPHIG;
    double MDL_CTPHI;
    double MDL_MUPRIME;
    double MDL_CCC;
    double AEWM1;
    double MDL_GF;
    double AS;
    double MDL_YMT;
    double MDL_YMTAU;
} params_r_;

// Read and set parameters from the param card
extern void load_param_card_(const char file[128], int len);

// Update only parameters that vary points by points
extern void update_as_param_();

// Update all parameters
extern void coup_();

// Matrix element
extern void ml5_1_sloopmatrix_(double p4[4][4], double ans[2][4]);
};

namespace WrapperSMOphiG {

ParametersWrapper::ParametersWrapper(const std::string& param_card) {
    const char* card = param_card.c_str();
    load_param_card_(card, 128);

    m_card_parameters["mdl_ctg"] = params_r_.MDL_CTG;
    m_card_parameters["mdl_ccc"] = params_r_.MDL_CCC;
    m_card_parameters["mdl_cphig"] = params_r_.MDL_CPHIG;
    m_card_parameters["mdl_ctphi"] = params_r_.MDL_CTPHI;
    m_card_parameters["mdl_c6"] = params_r_.MDL_C6;
    m_card_parameters["mdl_ch"] = params_r_.MDL_CH;
    m_card_parameters["mdl_lambda"] = params_r_.MDL_LAMBDA;
    m_card_parameters["aS"] = params_r_.AS;
}

void ParametersWrapper::cacheParameters() {
    params_r_.MDL_CTG = m_card_parameters["mdl_ctg"];
    params_r_.MDL_CCC = m_card_parameters["mdl_ccc"];
    params_r_.MDL_CPHIG = m_card_parameters["mdl_cphig"];
    params_r_.MDL_CTPHI = m_card_parameters["mdl_ctphi"];
    params_r_.MDL_C6 = m_card_parameters["mdl_c6"];
    params_r_.MDL_CH = m_card_parameters["mdl_ch"];
    params_r_.MDL_LAMBDA = m_card_parameters["mdl_lambda"];
    params_r_.AS = m_card_parameters["aS"];
}

void ParametersWrapper::cacheCouplings() {
    coup_();
    update_as_param_();
}

pp_hh_SM_OphiG::pp_hh_SM_OphiG(const std::string& param_card):
    params(new ParametersWrapper(param_card))
{}

std::map<std::pair<int, int>, double> pp_hh_SM_OphiG::compute(
        const std::pair<std::vector<double>, std::vector<double>>& initialMomenta,
        const std::vector<std::pair<int, std::vector<double>>>& finalState
        ) {
    Result result;
    if (finalState.size() != 2 || finalState[0].first != 25 || finalState[1].first != 25)
        return result;

    std::pair<int, int> initial_PIDs = std::make_pair(21, 21);

    double inputs[4][4] = {
        { initialMomenta.first[0], initialMomenta.first[1], initialMomenta.first[2], initialMomenta.first[3] },
        { initialMomenta.second[0], initialMomenta.second[1], initialMomenta.second[2], initialMomenta.second[3] },
        { finalState[0].second[0], finalState[0].second[1], finalState[0].second[2], finalState[0].second[3] },
        { finalState[1].second[0], finalState[1].second[1], finalState[1].second[2], finalState[1].second[3] }
    };
    
    double ans[2][4];

    ml5_1_sloopmatrix_(inputs, ans);

    result[initial_PIDs] = ans[0][1];

    return result;
}

std::shared_ptr<momemta::MEParameters> pp_hh_SM_OphiG::getParameters() {
    return params;
}

}

