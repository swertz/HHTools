#include <array>

#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

#include "EFTMEEvaluator.h"

#include "MatrixElements/pp_hh_5coup/SubProcesses/P1_Sigma_BSM_gg_hh_gg_hh/P1_Sigma_BSM_gg_hh_gg_hh.h"

#include "MatrixElements/pp_hh_all_MV/SubProcesses/P0_gg_hh/wrapper.h"
#include "MatrixElements/pp_hh_all_MV/SubProcesses/P1_gg_hh/wrapper.h"
#include "MatrixElements/pp_hh_all_MV/SubProcesses/P2_gg_hh/wrapper.h"
#include "MatrixElements/pp_hh_tree_MV/SubProcesses/P1_Sigma_modTEFT_H_gg_hh/P1_Sigma_modTEFT_H_gg_hh.h"

//typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double>> LorentzVector;

#define LORENTZ_TO_ARRAY(p4) std::vector<double>( { p4.E(), p4.Px(), p4.Py(), p4.Pz() } )

#define SQ(x) ((x)*(x))
#define CB(x) ((x)*(x)*(x))
#define QU(x) ((x)*(x)*(x)*(x))

const std::vector< std::map<std::string, double> > clustering_couplings;
const std::vector< std::string > clustering_coupling_names;

// couplings for "v1" benchmarks
const std::map< int, std::map<std::string, double> > benchmark_couplings {
    // SM
    {  0, { 
        { "mdl_c2" , 0      }, // c2
        { "mdl_a1" , 0      }, // cg
        { "mdl_a2" , 0      }, // c2g
        { "mdl_ctr", 1      }, // kl
        { "mdl_cy" , 1      }  // kt
    } },
    // node box
    { 1, { 
        { "mdl_c2" , 0      },
        { "mdl_a1" , 0      },
        { "mdl_a2" , 0      },
        { "mdl_ctr", 0.00001},
        { "mdl_cy" , 1      }
    } },
    // node 2
    { 2, { 
        { "mdl_c2" , -0.5   },
        { "mdl_a1" , 0      },
        { "mdl_a2" , 0      },
        { "mdl_ctr", 7.5    },
        { "mdl_cy" , 2.5    }
    } },
    // node 3
    { 3, { 
        { "mdl_c2" , -3     },
        { "mdl_a1" , -0.0816},
        { "mdl_a2" , 0.301  },
        { "mdl_ctr", 15.0   },
        { "mdl_cy" , 1.5    }
    } },
    // node 4
    { 4, { 
        { "mdl_c2" , 3.0    },
        { "mdl_a1" , 0      },
        { "mdl_a2" , 0      },
        { "mdl_ctr", 5.0    },
        { "mdl_cy" , 2.25   }
    } },
    // node 5
    { 5, { 
        { "mdl_c2" , -1.0   },
        { "mdl_a1" , -0.0956},
        { "mdl_a2" , 0.124  },
        { "mdl_ctr", 10.0   },
        { "mdl_cy" , 1.5    }
    } },
    // node 6
    { 6, { 
        { "mdl_c2" , 4      },
        { "mdl_a1" , -1     },
        { "mdl_a2" , -0.378 },
        { "mdl_ctr", 1      },
        { "mdl_cy" , 0.5    }
    } },
    // node 7
    { 7, { 
        { "mdl_c2" , 2.0    },
        { "mdl_a1" , -0.256 },
        { "mdl_a2" , -0.148 },
        { "mdl_ctr", 2.4    },
        { "mdl_cy" , 1.25   }
    } },
    // node 8
    { 8, { 
        { "mdl_c2" , 0.5    },
        { "mdl_a1" , 0.0    },
        { "mdl_a2" , 0.0    },
        { "mdl_ctr", 7.5    },
        { "mdl_cy" , 2.0    }
    } },
    // node 9
    { 9, { 
        { "mdl_c2" , 2.0    },
        { "mdl_a1" , -0.213 },
        { "mdl_a2" , -0.0893},
        { "mdl_ctr", 10.0   },
        { "mdl_cy" , 2.25   }
    } },
    // node 10
    { 10, { 
        { "mdl_c2" , 1.0    },
        { "mdl_a1" , -0.0743},
        { "mdl_a2" , -0.0668},
        { "mdl_ctr", 15.0   },
        { "mdl_cy" , 0.5    }
    } },
    // node 11
    { 11, { 
        { "mdl_c2" , 6.0    },
        { "mdl_a1" , -0.168 },
        { "mdl_a2" , -0.518 },
        { "mdl_ctr", -15.0  },
        { "mdl_cy" , 2.0    }
    } },
    // node 12
    { 12, { 
        { "mdl_c2" , 2.0    },
        { "mdl_a1" , -0.0616},
        { "mdl_a2" , -0.12  },
        { "mdl_ctr", 2.4    },
        { "mdl_cy" , 2.25   }
    } }
};

// Couplings for the "MV" operators - OphiG excepted
// Order matters!
const std::vector< std::map<std::string, double> > MV_noTree_couplings = {
    {
        { "mdl_ctg", 1 }
    },
    {
        { "mdl_ctphi", 1 }
    },
    {
        { "mdl_c6", 1 }
    },
    {
        { "mdl_ch", 1 }
    }
};
// Order matters!
const std::vector< std::string > MV_noTree_coupling_names = { "OtG", "Otphi", "O6", "OH" };

class HHEFTReweighter {
    public:
        HHEFTReweighter(std::string ME_dir=".") {
            m_evaluator_AC = std::make_shared<EFTMEEvaluator<pp_hh_5coup_BSM_gg_hh::P1_Sigma_BSM_gg_hh_gg_hh>>(ME_dir + "/pp_hh_5coup/Cards/param_card.dat", clustering_couplings, clustering_coupling_names);
            
            m_evaluator_MV_noTree = std::make_shared<EFTMEEvaluator<WrapperNoTree::pp_hh_noTree>>(ME_dir + "/pp_hh_all_MV/Cards/param_card", MV_noTree_couplings, MV_noTree_coupling_names);
            m_me_MV_SM_OphiG = std::make_shared<WrapperSMOphiG::pp_hh_SM_OphiG>(ME_dir + "/pp_hh_all_MV/Cards/param_card");
            m_me_MV_OphiG_ops = std::make_shared<WrapperOphiGOps::pp_hh_OphiG_ops>(ME_dir + "/pp_hh_all_MV/Cards/param_card");
            
            m_me_MV_OphiG_sq = std::make_shared<pp_hh_tree_MV_standalone_modTEFT_H::P1_Sigma_modTEFT_H_gg_hh>(ME_dir + "/pp_hh_tree_MV/Cards/param_card.dat");
        }

        ///////////////////////////////////////////////////////////////////
        ////////////////////  CLUSTERING MODEL ////////////////////////////
        ///////////////////////////////////////////////////////////////////

        double getBenchmarkME(const LorentzVector& h1, const LorentzVector& h2, const int bm) {
            // enforce the on-shell mass
            auto shell_h1 = put_on_shell(h1, 125);
            auto shell_h2 = put_on_shell(h2, 125);

            std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
            std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

            return (*m_evaluator_AC)(benchmark_couplings.at(bm), 21, 21, initials, finals);
        }

        double getACParamsME(const LorentzVector& h1, const LorentzVector& h2, const std::map<std::string, double>& params) {
            // enforce the on-shell mass
            auto shell_h1 = put_on_shell(h1, 125);
            auto shell_h2 = put_on_shell(h2, 125);

            std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
            std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

            return (*m_evaluator_AC)(params, 21, 21, initials, finals);
        }

        double computeXS5(int benchmark) {
            return computeXS5(benchmark_couplings.at(benchmark));
        }

        double computeXS5(const std::map<std::string, double>& params) {
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

        double getMVParamsME(const LorentzVector& h1, const LorentzVector& h2, const std::map<std::string, double>& params) {
            // MadLoop complains if Higgses are not precisely on shell
            auto shell_h1 = put_on_shell(h1, 125);
            auto shell_h2 = put_on_shell(h2, 125);

            std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
            std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

            return (*m_evaluator_MV_noTree)(params, 21, 21, initials, finals);
        }

        double getMVTermME(const LorentzVector& h1, const LorentzVector& h2, int op_1, int op_2) {
            auto shell_h1 = put_on_shell(h1, 125);
            auto shell_h2 = put_on_shell(h2, 125);

            std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
            std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

            return (*m_evaluator_MV_noTree)(op_1, op_2, 21, 21, initials, finals);
        }
        
        // All terms not involving OphiG
        void getAllMVTermsME(const LorentzVector& h1, const LorentzVector& h2, std::vector<double> &weights, double alpha_s=0) {
            auto shell_h1 = put_on_shell(h1, 125);
            auto shell_h2 = put_on_shell(h2, 125);

            std::pair< std::vector<double>, std::vector<double> > initials = getInitialsFromHiggses(shell_h1, shell_h2);
            std::vector< std::pair<int, std::vector<double>> > finals = { { 25, LORENTZ_TO_ARRAY(shell_h1) }, { 25, LORENTZ_TO_ARRAY(shell_h2) } };

            m_evaluator_MV_noTree->computeTerms(21, 21, initials, finals, weights, alpha_s);
        }

        // All terms involving OphiG, Mr. Pain in the Ass
        void getCustomMVTermsME(const LorentzVector& h1, const LorentzVector& h2, double &weight_sm_ophig, double & weight_ophig_sq, std::vector<double> &weights_ophig_ops, double alpha_s=0) {
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
        std::pair< std::vector<double>, std::vector<double> > getInitialsFromHiggses(const LorentzVector& h1, const LorentzVector& h2) const {
            double E = h1.E() + h2.E();
            double Pz = h1.Pz() + h2.Pz();

            double q1 = std::abs(0.5 * (E + Pz));
            double q2 = std::abs(0.5 * (E - Pz));

            return { { q1, 0, 0, q1 }, { q2, 0, 0, -q2 } };
        }

        // Change a 4-vector's mass by adjusting its energy, keeping its momentum
        LorentzVector put_on_shell(const LorentzVector& v, double mass) {
            LorentzVector shell_v = v;
            shell_v.SetE( sqrt(mass * mass + v.P2()) );
            return shell_v;
        }


    private:

        std::shared_ptr<EFTMEEvaluatorBase> m_evaluator_AC;
        std::shared_ptr<EFTMEEvaluatorBase> m_evaluator_MV_noTree;
        std::shared_ptr<momemta::MatrixElement> m_me_MV_SM_OphiG;
        std::shared_ptr<momemta::MatrixElement> m_me_MV_OphiG_ops;
        std::shared_ptr<momemta::MatrixElement> m_me_MV_OphiG_sq;
};

HHEFTReweighter& getHHEFTReweighter(std::string ME_dir=".") {
    static HHEFTReweighter m_reweighter(ME_dir);
    return m_reweighter;
}
