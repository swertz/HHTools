#pragma once

#include <string>
#include <iostream>
#include <memory>
#include <algorithm>
#include <stdexcept>
#include <chrono>
#include <map>
#include <utility>

#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>

#include <TFile.h>
#include <TEfficiency.h>
#include <TAxis.h>
#include <TH1F.h>

#include "utils.h"

#define N_TOYS 5000
#define BETA_PRIOR_ALPHA 1.0
#define BETA_PRIOR_BETA 1.0
#define DIRI_PRIOR_ALPHA 1.0
//#define N_FLAV 5
#define N_FLAV 3

struct CacheKey {
    LorentzVector jet1;
    LorentzVector jet2;
    float BDTout;
    std::string syst;

    bool operator==(const CacheKey &rhs) const {
        return jet1 == rhs.jet1 && jet2 == rhs.jet2 && BDTout == rhs.BDTout && syst == rhs.syst;
    }
};

namespace std {
    template<>
    struct hash<CacheKey> {
        std::size_t operator()(const CacheKey& k) const {
            std::size_t m_hash = 0;
            hash_combine(m_hash, k.jet1);
            hash_combine(m_hash, k.jet2);
            hash_combine(m_hash, k.BDTout);
            hash_combine(m_hash, k.syst);
            return m_hash;
        }
    };
}

std::pair<double, double> GetPosteriorAlphaBeta(const TEfficiency& teff, std::size_t bin, double p_alpha=BETA_PRIOR_ALPHA, double p_beta=BETA_PRIOR_BETA);

class FWBTagEfficiencyOnBDT {
    public:

        FWBTagEfficiencyOnBDT() = delete;

        FWBTagEfficiencyOnBDT(const std::string& btag_efficiencies, const std::string& btag_sf, const std::string& flavor_fraction);
        
        double propagate_linear(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, const std::string& syst);

        double monte_carlo_quantile(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, double proba, unsigned int nToys);

        void monte_carlo_quantiles(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, const std::vector<double>& probas, unsigned int nToys, std::vector<double>& quantiles);

        /*
         * Return error of a TEfficiency bin (specified by 'bin'):
         * If 'syst' is "dyStat(up|down)", return high or low error (with sign) in the bin of the nominal object, as computed by TEfficiency
         * Otherwise, return difference between the systematic value and the nominal value in that bin.
         * I.e. the result should(can) be positive for "up" variations and negative for "down" variations
         * If the systematics is not known, return 0.
         */
        double get_sigma(const std::string& syst, std::size_t bin, const std::map<std::string, std::unique_ptr<TEfficiency>>& teff_map);

        double get(const LorentzVector& jet1, const LorentzVector& jet2, float BDTout, std::string syst="nominal");
        
        double get_cached(const LorentzVector& jet1, const LorentzVector& jet2, float BDTout, const std::string& syst="nominal");

        void clear_cache() {
            m_cache.clear();
        }

    private:
        
        class systematics_error: public std::runtime_error {
            using std::runtime_error::runtime_error;
        };
        
        /*
         * Represent a matrix over two flavours as a one-dimensional vector
         */
        std::size_t flavor_index_map(uint8_t flav1, uint8_t flav2);
        
        /*
         * Retrieve the Dirichlet alphas for the fractions in a particular bin,
         * fill 'alphas' using the one dimensional representation provided by 'flavor_index_map()'
         */
        void fill_fraction_alphas(std::size_t bin, std::array<double, N_FLAV * N_FLAV>& alphas);

        /*
         * Retrieve the Beta's alpha and beta for the efficiencies in a particular bin,
         * Fill 'alpha_beta' with pairs; map is indexed by flavor
         */
        void fill_btag_alpha_betas(std::size_t bin, std::array<std::pair<double, double>, 6>& alpha_betas);

        /*
         * Return bin in the btagging efficiency for a given jet
         * Assumes all the efficiencies have the same binning!
         */
        std::size_t get_btag_bin(const LorentzVector& jet);

        /*
         * Return bin in the fractions histogram for a given BDT value
         * Assumes all the fractions have the same binning!
         */
        std::size_t get_frac_bin(float BDTout);

        std::size_t get_btag_sf_bin(const LorentzVector& jet);
        double get_btag_sf(uint8_t flav, std::size_t bin);
        double get_btag_sf_error(uint8_t flav, std::size_t bin, const std::string& syst);

        std::pair<double, double> get_range(const TAxis& h);

        double clip(double var, const std::pair<double, double>& range); 
        
        std::unordered_map<CacheKey, double> m_cache;

        // Regular
        std::vector<uint8_t> flavors {0, 4, 5};
        std::map<uint8_t, std::string> flavors_to_string {{0, "l"}, {4, "c"}, {5, "b"}};

        // Split light
        //std::vector<uint8_t> flavors {0, 1, 21, 4, 5};
        //std::map<uint8_t, std::string> flavors_to_string {{0, "n"}, {1, "q"}, {21, "g"}, {4, "c"}, {5, "b"}};

        //std::vector<std::string> systematics { "nominal" };
        std::vector<std::string> systematics_btag { "nominal", 
            "puup", "pdfup", "jecup", "jerup",
            "pudown", "pdfdown", "jecdown", "jerdown",
            "scaleUncorr0", "scaleUncorr1", "scaleUncorr2", "scaleUncorr3", "scaleUncorr4", "scaleUncorr5",
            "jecabsoluteflavmapup", "jecabsoluteflavmapdown",
            "jecabsolutempfbiasup", "jecabsolutempfbiasdown",
            "jecabsolutescaleup",   "jecabsolutescaledown",
            "jecabsolutestatup",    "jecabsolutestatdown",
            "jecflavorqcdup",       "jecflavorqcddown",
            "jecfragmentationup",   "jecfragmentationdown",
            "jecpileupdatamcup",    "jecpileupdatamcdown",
            "jecpileupptbbup",      "jecpileupptbbdown",
            "jecpileupptec1up",     "jecpileupptec1down",
            "jecpileupptec2up",     "jecpileupptec2down",
            "jecpileuppthfup",      "jecpileuppthfdown",
            "jecpileupptrefup",     "jecpileupptrefdown",
            "jecrelativebalup",     "jecrelativebaldown",
            "jecrelativefsrup",     "jecrelativefsrdown",
            "jecrelativejerec1up",  "jecrelativejerec1down",
            "jecrelativejerec2up",  "jecrelativejerec2down",
            "jecrelativejerhfup",   "jecrelativejerhfdown",
            "jecrelativeptbbup",    "jecrelativeptbbdown",
            "jecrelativeptec1up",   "jecrelativeptec1down",
            "jecrelativeptec2up",   "jecrelativeptec2down",
            "jecrelativepthfup",    "jecrelativepthfdown",
            "jecrelativestatecup",  "jecrelativestatecdown",
            "jecrelativestatfsrup", "jecrelativestatfsrdown",
            "jecrelativestathfup",  "jecrelativestathfdown",
            "jecsinglepionecalup",  "jecsinglepionecaldown",
            "jecsinglepionhcalup",  "jecsinglepionhcaldown",
            "jectimeptetaup",       "jectimeptetadown",
            "pdfqqup", "pdfqqdown",
            "pdfggup", "pdfggdown",
            "pdfqgup", "pdfqgdown"
        };
        std::vector<std::string> systematics_fractions = systematics_btag; 

        // Indexed as [pair(flav1, flav2)][syst]
        std::map<std::pair<uint8_t, uint8_t>, std::map<std::string, std::unique_ptr<TEfficiency>>> m_fractions;
        // Used for the Bayesian calculations of the intervals and covariances (vectors: one entry per bin in the fractions TEfficiency)
        std::map<std::pair<uint8_t, uint8_t>, std::vector<double>> m_fractions_alphas;
        std::vector<double> m_fractions_alpha_zeros;

        // Indexed as [flav][syst]
        std::map<uint8_t, std::map<std::string, std::unique_ptr<TEfficiency>>> m_btagging_eff;
        
        // Indexed as [flav]
        std::map<uint8_t, std::unique_ptr<TH1>> m_btagging_sf;
        std::map<uint8_t, std::unique_ptr<TH1>> m_btagging_sf_error;
            
        std::shared_ptr<gsl_rng> r;
};
