#include "reweight_me.h"

HHEFTReweighter& getHHEFTReweighter(std::string ME_dir) {
    static HHEFTReweighter m_reweighter(ME_dir);
    return m_reweighter;
}

///////////////////////////////////////////////////////////////////
////////////////////  CLUSTERING MODEL ////////////////////////////
///////////////////////////////////////////////////////////////////

double HHEFTReweighter::getBenchmarkME(const LorentzVector& h1, const LorentzVector& h2, const int bm, double alpha_s) {
    // enforce the on-shell mass
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    return (*m_evaluator_AC)(benchmark_couplings_v3.at(bm), 21, 21, initials, finals, alpha_s);
}

double HHEFTReweighter::getACParamsME(const LorentzVector& h1, const LorentzVector& h2, const std::map<std::string, double>& params, double alpha_s) {
    // enforce the on-shell mass
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    return (*m_evaluator_AC)(params, 21, 21, initials, finals, alpha_s);
}

double HHEFTReweighter::computeXS5(int benchmark) {
    return computeXS5(benchmark_couplings_v3.at(benchmark));
}

double HHEFTReweighter::computeXS5(const std::map<std::string, double>& params) {
    static std::array<double, 15> coefs { 2.09078, 10.1517, 0.282307, 0.101205, 1.33191, -8.51168, -1.37309, 2.82636, 1.45767, -4.91761, -0.675197, 1.86189, 0.321422, -0.836276, -0.568156 };
    
    double result = 
        coefs[0] * QU(params.at("mdl_cy")) + coefs[1] * SQ(params.at("mdl_c2")) + 
        ( coefs[2] * SQ(params.at("mdl_cy")) + coefs[3] * SQ(params.at("mdl_a1")) ) 
                * SQ(params.at("mdl_ctr")) + 
        coefs[4] * SQ(params.at("mdl_a2")) + 
        ( coefs[5] * params.at("mdl_c2") + coefs[6] * params.at("mdl_cy") * params.at("mdl_ctr") ) 
                * SQ(params.at("mdl_cy")) + 
        ( coefs[7] * params.at("mdl_cy") * params.at("mdl_ctr") + 
            coefs[8] * params.at("mdl_a1") * params.at("mdl_ctr") ) 
                * params.at("mdl_c2") + 
        coefs[9] * params.at("mdl_c2") * params.at("mdl_a2") + 
        ( coefs[10] * params.at("mdl_a1")*params.at("mdl_ctr") + 
            coefs[11] * params.at("mdl_a2") ) 
                * SQ(params.at("mdl_cy")) +
        ( coefs[12] * params.at("mdl_ctr") * params.at("mdl_a1") + 
            coefs[13] * params.at("mdl_a2") ) 
                * params.at("mdl_cy") * params.at("mdl_ctr") + 
        coefs[14] * params.at("mdl_a1") * params.at("mdl_a2") * params.at("mdl_ctr");
    return result;
}

///////////////////////////////////////////////////////////////////
////////////////  MALTONI ET AL. MODEL ////////////////////////////
///////////////////////////////////////////////////////////////////

double HHEFTReweighter::getMVParamsME(const LorentzVector& h1, const LorentzVector& h2, const std::map<std::string, double>& params, double alpha_s) {
    // MadLoop complains if Higgses are not precisely on shell
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    return (*m_evaluator_MV_noTree)(params, 21, 21, initials, finals, alpha_s);
}

double HHEFTReweighter::getMVTermME(const LorentzVector& h1, const LorentzVector& h2, int op_1, int op_2, double alpha_s) {
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    return (*m_evaluator_MV_noTree)(op_1, op_2, 21, 21, initials, finals, alpha_s);
}

// All terms not involving OphiG
void HHEFTReweighter::getAllMVTermsME(const LorentzVector& h1, const LorentzVector& h2, std::vector<double> &weights, double alpha_s) {
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    m_evaluator_MV_noTree->computeTerms(21, 21, initials, finals, weights, alpha_s);
}

// All terms involving OphiG, Mr. Pain in the Ass
void HHEFTReweighter::getCustomMVTermsME(const LorentzVector& h1, const LorentzVector& h2, double &weight_sm_ophig, double & weight_ophig_sq, std::vector<double> &weights_ophig_ops, double alpha_s) {
    auto shell_h1 = put_on_shell(h1, 125);
    auto shell_h2 = put_on_shell(h2, 125);

    std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
    std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

    // First reset all couplings to 0
    for (const auto& op: MV_noTree_couplings) {
        for (const auto& param: op) {
            m_me_MV_SM_OphiG->getParameters()->setParameter(param.first, 0);
            m_me_MV_OphiG_ops->getParameters()->setParameter(param.first, 0);
        }
    }                
    
    // First SM-OphiG interference
    if (alpha_s > 0)
        m_me_MV_SM_OphiG->getParameters()->setParameter("as", alpha_s);
    m_me_MV_SM_OphiG->getParameters()->setParameter("mdl_cphig", 1);
    weight_sm_ophig = m_me_MV_SM_OphiG->compute(initials, finals)[{21, 21}];
    
    // Then OphiG squared -- note the different parameter names
    // Here we assume the param card is set correctly for the other couplings
    if (alpha_s > 0)
        m_me_MV_OphiG_sq->getParameters()->setParameter("aS", alpha_s);
    m_me_MV_OphiG_sq->getParameters()->setParameter("mdl_CphiG", 1);
    weight_ophig_sq = m_me_MV_OphiG_sq->compute(initials, finals)[{21, 21}];
    
    // Then OphiG - other operators
    m_me_MV_OphiG_ops->getParameters()->setParameter("mdl_cphig", 1);
    if (alpha_s > 0)
        m_me_MV_OphiG_ops->getParameters()->setParameter("as", alpha_s);
    
    for (int i = 0; i < MV_noTree_couplings.size(); i++) {    
        const auto &op = MV_noTree_couplings.at(i);
        for (const auto& param: op) {
            m_me_MV_OphiG_ops->getParameters()->setParameter(param.first, param.second);
        }
        
        double f_11 = m_me_MV_OphiG_ops->compute(initials, finals)[{21, 21}];
        
        // The matrix element contains ( (some crap) + (OphiG_tree * OX) )
        // Since we want only the second part, we have to subtract from the result the ME evaluated 
        // with OX set to zero
        
        for (const auto& param: op) {
            m_me_MV_OphiG_ops->getParameters()->setParameter(param.first, 0);
        }
        
        double f_01 = m_me_MV_OphiG_ops->compute(initials, finals)[{21, 21}];

        weights_ophig_ops.at(i) = f_11 - f_01;
    }
}

///////////////////////////////////////////////////////////////////
////////////////////////  HELPER STUFF ////////////////////////////
///////////////////////////////////////////////////////////////////

/*
 * Compute initial parton 4-vectors (in array form) from the Lorentz vectors of the 2 Higgses
 * NOTE: assumes the Higgses do not have any ISR!
 */
std::pair< std::vector<double>, std::vector<double> > HHEFTReweighter::getInitialsFromHiggses(const LorentzVector& h1, const LorentzVector& h2) const {
    double E = h1.E() + h2.E();
    double Pz = h1.Pz() + h2.Pz();

    double q1 = std::abs(0.5 * (E + Pz));
    double q2 = std::abs(0.5 * (E - Pz));

    return { { q1, 0, 0, q1 }, { q2, 0, 0, -q2 } };
}

// Change a 4-vector's mass by adjusting its energy, keeping its momentum
LorentzVector HHEFTReweighter::put_on_shell(const LorentzVector& v, double mass) const {
    LorentzVector shell_v = v;
    shell_v.SetE( sqrt(mass * mass + v.P2()) );
    return shell_v;
}
