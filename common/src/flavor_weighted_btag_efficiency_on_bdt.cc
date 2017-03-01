#include <cmath>

#include "flavor_weighted_btag_efficiency_on_bdt.h"

std::pair<double, double> GetPosteriorAlphaBeta(const TEfficiency& teff, std::size_t bin, double p_alpha, double p_beta) {
    double sumw = teff.GetTotalHistogram()->GetBinContent(bin);
    double sumw2 = teff.GetTotalHistogram()->GetSumw2()->At(bin);
    double passw = teff.GetPassedHistogram()->GetBinContent(bin);
    double alpha = passw * sumw / sumw2 + p_alpha;
    double beta = (sumw - passw) * sumw / sumw2 + p_beta;
    return std::make_pair(alpha, beta);
}
        
FWBTagEfficiencyOnBDT::FWBTagEfficiencyOnBDT(const std::string& btag_efficiencies, const std::string& btag_sf, const std::string& flavor_fraction) {
    std::cout << "Initializing flavour-weighted reweighter." << std::endl;
        
    std::unique_ptr<TFile> file(TFile::Open(btag_efficiencies.c_str()));
    if (!file || !file->IsOpen() ){
        std::cerr << "Error: could not open file " << btag_efficiencies << std::endl;
        exit(1);
    }

    for (const auto& flav: flavors) {
        for (const auto& syst: systematics_btag) {
            std::string name;
            name = "btagging_eff_on_" + flavors_to_string[flav];
            if (syst != "nominal")
                name += "__" + syst;

            std::unique_ptr<TEfficiency> btagging_eff(static_cast<TEfficiency*>(file->Get(name.c_str())));
            if (!btagging_eff) {
                std::cerr << "Error: could not find TEfficiency \"" << name << "\" in file " << btag_efficiencies << std::endl;
                exit(1);
            }
            btagging_eff->SetUseWeightedEvents();
            btagging_eff->SetStatisticOption(TEfficiency::kBJeffrey);

            btagging_eff->SetDirectory(nullptr);
            m_btagging_eff[flav].emplace(syst, std::move(btagging_eff));
        }
    }

    file.reset(TFile::Open(flavor_fraction.c_str()));
    if (!file || !file->IsOpen() ){
        std::cerr << "Error: could not open file " << flavor_fraction << std::endl;
        exit(1);
    }

    for (const auto& flav1: flavors) {
        for (const auto& flav2: flavors) {
            std::pair<uint8_t, uint8_t> key = std::make_pair(flav1, flav2);

            for (const auto& syst: systematics_fractions) {

                std::string name = flavors_to_string[flav1] + flavors_to_string[flav2] + "_frac";
                if (syst != "nominal")
                    name += "__" + syst;

                std::unique_ptr<TEfficiency> fraction(static_cast<TEfficiency*>(file->Get(name.c_str())));
                if (!fraction) {
                    std::cerr << "Error: could not find TEfficiency \"" << name << "\" in file " << flavor_fraction << std::endl;
                    exit(1);
                }
                    
                if (syst == "nominal") {
                    // Compute the alpha_i of the Dirichlet for the flavour fractions,
                    // for each bin in the BDT.
                    // Inspired by https://root.cern.ch/doc/master/TEfficiency_8cxx_source.html#l02467
                    std::size_t n_bins = fraction->GetTotalHistogram()->GetNbinsX();
                    m_fractions_alpha_zeros.resize(n_bins, 0);
                    for (std::size_t bin = 1; bin <= n_bins; bin++) {
                        double sumw = fraction->GetTotalHistogram()->GetBinContent(bin);
                        double sumw2 = fraction->GetTotalHistogram()->GetSumw2()->At(bin);
                        double passw = fraction->GetPassedHistogram()->GetBinContent(bin);
                        double alpha = passw * sumw / sumw2 + DIRI_PRIOR_ALPHA;
                        m_fractions_alphas[std::make_pair(flav1, flav2)].push_back(alpha);
                        m_fractions_alpha_zeros[bin - 1] += alpha;
                    }
                }
                
                fraction->SetDirectory(nullptr);
                m_fractions[key].emplace(syst, std::move(fraction));
            }
        }
    }

    // We want a prior for the Dirichlet, which gives us "alpha" and "beta" of the marginal
    // Beta distributions for each fraction:
    for (auto& frac: m_fractions) {
        frac.second["nominal"]->SetStatisticOption(TEfficiency::kBBayesian);
        frac.second["nominal"]->SetBetaAlpha(DIRI_PRIOR_ALPHA);
        frac.second["nominal"]->SetBetaBeta(DIRI_PRIOR_ALPHA * (m_fractions_alphas.size() - 1));
    }
    
    // Load B-tagging scale factors
    file.reset(TFile::Open(btag_sf.c_str()));
    if (!file || !file->IsOpen() ){
        std::cerr << "Error: could not open file " << btag_sf << std::endl;
        exit(1);
    }
    
    for (const auto& flav: flavors) {
        std::string name = "btag_sf_" + flavors_to_string[flav];
        std::unique_ptr<TH1> nominal_sf(static_cast<TH1*>(file->Get(name.c_str())));
        if (!nominal_sf) {
            std::cerr << "Error: could not find TH1 \"" << name << "\" in file " << btag_sf << std::endl;
            exit(1);
        }
        nominal_sf->SetDirectory(nullptr);
        m_btagging_sf.emplace(flav, std::move(nominal_sf));
        
        name = "btag_sf_error_" + flavors_to_string[flav];
        std::unique_ptr<TH1> error_sf(static_cast<TH1*>(file->Get(name.c_str())));
        if (!error_sf) {
            std::cerr << "Error: could not find TH1 \"" << name << "\" in file " << btag_sf << std::endl;
            exit(1);
        }
        error_sf->SetDirectory(nullptr);
        m_btagging_sf_error.emplace(flav, std::move(error_sf));
    }
    
    r = std::shared_ptr<gsl_rng>(gsl_rng_alloc(gsl_rng_mt19937), gsl_rng_free);
}
        
double FWBTagEfficiencyOnBDT::get_cached(const LorentzVector& jet1, const LorentzVector& jet2, float BDTout, const std::string& syst) {
    CacheKey key { jet1, jet2, BDTout, syst };
    
    auto it = m_cache.find(key);
    
    if (it == m_cache.end()) {
        double result = get(jet1, jet2, BDTout, syst);
        m_cache.emplace(key, result);
        return result;
    } else {
        return it->second;
    }
}

double FWBTagEfficiencyOnBDT::get(const LorentzVector& jet1, const LorentzVector& jet2, float BDTout, std::string syst) {

    /*
     * Some assumptions:
     *  - b-tag efficiencies are binning in pt and eta for all jets
     *  - flavor fractions are binned in BDT
     * Special systematics: "dyStat(up|down)" -> take the statistical error on the fractions/efficiencies as the systematic uncertainty
     * Special systematics: "dyScaleUncorr?" -> take the "scaleUncorr?" efficiencies/fractions
     * If the given systematics has not been computed for the efficiencies or fractions, the nominal value is returned.
     */

    std::size_t btag_bin_jet1 = get_btag_bin(jet1);
    std::size_t btag_bin_jet2 = get_btag_bin(jet2);
    std::size_t btag_sf_bin_jet1 = get_btag_sf_bin(jet1);
    std::size_t btag_sf_bin_jet2 = get_btag_sf_bin(jet2);
    std::size_t frac_bin = get_frac_bin(BDTout);

    double nominal_weight = 0;
    for (const auto& flav1: flavors) {
        double jet1_btagging_eff = m_btagging_eff[flav1]["nominal"]->GetEfficiency(btag_bin_jet1);
        for (const auto& flav2: flavors) {
            double jet2_btagging_eff = m_btagging_eff[flav2]["nominal"]->GetEfficiency(btag_bin_jet2);

            const auto& fraction_eff = m_fractions[std::make_pair(flav1, flav2)]["nominal"];
            double fraction = fraction_eff->GetEfficiency(frac_bin);

            nominal_weight += fraction * jet1_btagging_eff * jet2_btagging_eff * get_btag_sf(flav1, btag_sf_bin_jet1) * get_btag_sf(flav2, btag_sf_bin_jet2);
        }
    }
    //std::cout << "nominal weight: " << nominal_weight << std::endl;
    //std::cout << "quantile 50%: " << monte_carlo_quantile(get_btag_bin(jet1), get_btag_bin(jet2), get_frac_bin(BDTout), 0.5, 10000) << std::endl;
    
    // Scale uncertainty: special treatment
    // If it's a "regular" scale, return the nominal value
    // If it's a "DY" scale, return the modified weight, but not forget to rename
    // the syst string to match the efficiencies/fractions names
    if (syst.find("scale") != std::string::npos) {
        syst = "nominal";
    } else if (syst.find("dyScale") == 0) {
        syst.replace(0, std::string("dyScale").size(), "scale");
    }

    // Nominal value
    if (syst == "nominal")
        return std::max(0., nominal_weight);
    
    // Systematics is the Stat. error => compute the quantiles using MC
    if (syst.find("dyStat") != std::string::npos) {
        double proba;
        if (syst.find("up") != std::string::npos)
            proba = 0.84;
        else if (syst.find("down") != std::string::npos)
            proba = 0.16;
        else
            throw systematics_error("Could not understand up or down variation from " + syst);
        double val = monte_carlo_quantile(btag_bin_jet1, btag_bin_jet2, btag_sf_bin_jet1, btag_sf_bin_jet2, frac_bin, proba, N_TOYS);
        //double variance = propagate_variance(jet1, jet2, BDTout, syst);
        //std::cout << "nominal: " << nominal_weight << ", variance: " << variance << ", quantile: " << std::abs(nominal_weight - val) << std::endl;
        return std::max(0., val);
    }

    // Other systematics => propagate errors
    double error = propagate_linear(btag_bin_jet1, btag_bin_jet2, btag_sf_bin_jet1, btag_sf_bin_jet2, frac_bin, syst);
    //std::cout << "Systematics: " << syst << ", nominal: " << nominal_weight << ", error: " << error << std::endl;
    return std::max(0., nominal_weight + error);
}

double FWBTagEfficiencyOnBDT::get_sigma(const std::string& syst, std::size_t bin, const std::map<std::string, std::unique_ptr<TEfficiency>>& teff_map) {
    if (syst == "dyStatup")
        return teff_map.at("nominal")->GetEfficiencyErrorUp(bin);
    else if (syst == "dyStatdown")
        return -teff_map.at("nominal")->GetEfficiencyErrorLow(bin);
    if (teff_map.find(syst) != teff_map.end())
        return teff_map.at(syst)->GetEfficiency(bin) - teff_map.at("nominal")->GetEfficiency(bin) ;
    else
        return 0;
}

double FWBTagEfficiencyOnBDT::propagate_linear(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, const std::string& syst) {
    // Used to get correct sign for btagging SF errors
    double btag_sf_factor = 0;
    if (syst.find("jjbtag") != std::string::npos) {
        if (syst.find("up") != std::string::npos)
            btag_sf_factor = 1;
        else
            btag_sf_factor = -1;
    }
    
    double err = 0;

    for (const auto& flav1: flavors) {
        for (const auto& flav2: flavors) {
            // Btagging SF related part
            if (btag_sf_factor != 0) {
                // dS_i
                err += get_btag_sf(flav2, jet2_sf_bin) * 
                       m_btagging_eff[flav1]["nominal"]->GetEfficiency(jet1_eff_bin) * 
                       m_btagging_eff[flav2]["nominal"]->GetEfficiency(jet2_eff_bin) * 
                       m_fractions[std::make_pair(flav1, flav2)]["nominal"]->GetEfficiency(frac_bin) *
                       get_btag_sf_error(flav1, jet1_sf_bin, syst) * btag_sf_factor;
                // dS'_i
                err += get_btag_sf(flav2, jet1_sf_bin) * 
                       m_btagging_eff[flav2]["nominal"]->GetEfficiency(jet1_eff_bin) * 
                       m_btagging_eff[flav1]["nominal"]->GetEfficiency(jet2_eff_bin) * 
                       m_fractions[std::make_pair(flav2, flav1)]["nominal"]->GetEfficiency(frac_bin) *
                       get_btag_sf_error(flav1, jet2_sf_bin, syst) * btag_sf_factor;
            }

            // Non-SF related part
            
            // dE_i
            err += get_btag_sf(flav1, jet1_sf_bin) * 
                   get_btag_sf(flav2, jet2_sf_bin) * 
                   m_btagging_eff[flav2]["nominal"]->GetEfficiency(jet2_eff_bin) * 
                   m_fractions[std::make_pair(flav1, flav2)]["nominal"]->GetEfficiency(frac_bin) *
                   get_sigma(syst, jet1_eff_bin, m_btagging_eff[flav1]);
            // dE'_i
            err += get_btag_sf(flav2, jet1_sf_bin) * 
                   get_btag_sf(flav1, jet2_sf_bin) * 
                   m_btagging_eff[flav2]["nominal"]->GetEfficiency(jet1_eff_bin) * 
                   m_fractions[std::make_pair(flav2, flav1)]["nominal"]->GetEfficiency(frac_bin) *
                   get_sigma(syst, jet2_eff_bin, m_btagging_eff[flav1]);

            // dF_ij
            err += get_btag_sf(flav1, jet1_sf_bin) * 
                   get_btag_sf(flav2, jet2_sf_bin) * 
                   m_btagging_eff[flav1]["nominal"]->GetEfficiency(jet1_eff_bin) * 
                   m_btagging_eff[flav2]["nominal"]->GetEfficiency(jet2_eff_bin) * 
                   get_sigma(syst, frac_bin, m_fractions[std::make_pair(flav1, flav2)]);
        }
    }

    return err;
}

double FWBTagEfficiencyOnBDT::monte_carlo_quantile(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, double proba, unsigned int nToys) {
    std::vector<double> quantile(1);
    monte_carlo_quantiles(jet1_eff_bin, jet2_eff_bin, jet1_sf_bin, jet2_sf_bin, frac_bin, { proba }, nToys, quantile);
    return quantile[0];
}

void FWBTagEfficiencyOnBDT::monte_carlo_quantiles(std::size_t jet1_eff_bin, std::size_t jet2_eff_bin, std::size_t jet1_sf_bin, std::size_t jet2_sf_bin, std::size_t frac_bin, const std::vector<double>& probas, unsigned int nToys, std::vector<double>& quantiles) {
    static std::vector<double> results(nToys);
    std::size_t nFlav = flavors.size();

    static std::array<double, N_FLAV * N_FLAV> fractions;
    // Compute the "alphas" of the fractions Dirichlet
    static std::array<double, N_FLAV * N_FLAV> frac_alphas;
    fill_fraction_alphas(frac_bin, frac_alphas);

    // Compute the alpha/beta of the efficiencies Betas
    static std::array<std::pair<double, double>, 6> jet1_eff_alpha_beta;
    fill_btag_alpha_betas(jet1_eff_bin, jet1_eff_alpha_beta);
    static std::array<std::pair<double, double>, 6> jet2_eff_alpha_beta;
    fill_btag_alpha_betas(jet2_eff_bin, jet2_eff_alpha_beta);

    double weight, jet1_eff_alpha, jet1_eff_beta, jet2_eff_alpha, jet2_eff_beta, eps_1, eps_2;
    
    // Generate the toys
    for (unsigned int i = 0; i < nToys; i++) {
        weight = 0;
        
        // Generate the fractions as a Dirichlet, store in 'fractions'
        gsl_ran_dirichlet(r.get(), N_FLAV * N_FLAV, frac_alphas.data(), fractions.data());

        for (const auto& flav1: flavors) {
            for (const auto& flav2: flavors) {
                jet1_eff_alpha = jet1_eff_alpha_beta[flav1].first;
                jet1_eff_beta = jet1_eff_alpha_beta[flav1].second;
                jet2_eff_alpha = jet2_eff_alpha_beta[flav2].first;
                jet2_eff_beta = jet2_eff_alpha_beta[flav2].second;

                if (flav1 == flav2 && jet1_eff_bin == jet2_eff_bin) {
                    eps_1 = gsl_ran_beta(r.get(), jet1_eff_alpha, jet1_eff_beta);
                    weight += eps_1 * eps_1 * 
                        get_btag_sf(flav1, jet1_sf_bin) * get_btag_sf(flav2, jet2_sf_bin) *
                        fractions[flavor_index_map(flav1, flav2)];
                } else {
                    eps_1 = gsl_ran_beta(r.get(), jet1_eff_alpha, jet1_eff_beta);
                    eps_2 = gsl_ran_beta(r.get(), jet2_eff_alpha, jet2_eff_beta);
                    eps_1 *= get_btag_sf(flav1, jet1_sf_bin);
                    eps_2 *= get_btag_sf(flav2, jet2_sf_bin);
                    weight += eps_1 * eps_2 * fractions[flavor_index_map(flav1, flav2)];
                }
            }
        }
        results[i] = weight;
    }
    
    quantiles = Quantile(results, probas);
}

std::size_t FWBTagEfficiencyOnBDT::flavor_index_map(uint8_t flav1, uint8_t flav2) {
    return get_vector_index(flavors, flav1) + flavors.size() * get_vector_index(flavors, flav2);
}

void FWBTagEfficiencyOnBDT::fill_fraction_alphas(std::size_t bin, std::array<double, N_FLAV * N_FLAV>& alphas) {
    for (const auto& flav1: flavors) {
        for (const auto& flav2: flavors) {
            alphas.at(flavor_index_map(flav1, flav2)) = m_fractions_alphas[std::make_pair(flav1, flav2)][bin - 1];
        }
    }
}

void FWBTagEfficiencyOnBDT::fill_btag_alpha_betas(std::size_t bin, std::array<std::pair<double, double>, 6>& alpha_betas) {
    for (const auto& flav: flavors) {
        alpha_betas[flav] = GetPosteriorAlphaBeta(*m_btagging_eff[flav]["nominal"], bin);
    }
}

std::size_t FWBTagEfficiencyOnBDT::get_btag_bin(const LorentzVector& jet) {
    const auto& btag_eff = m_btagging_eff[flavors.at(0)]["nominal"];
    return btag_eff->FindFixBin(jet.Pt(), std::abs(jet.Eta()));
}

std::size_t FWBTagEfficiencyOnBDT::get_frac_bin(float BDTout) {
    const auto& fraction_eff = m_fractions[std::make_pair(flavors.at(0), flavors.at(0))]["nominal"];
    return fraction_eff->FindFixBin(clip(BDTout, get_range(*fraction_eff->GetTotalHistogram()->GetXaxis())));
}
 
std::size_t FWBTagEfficiencyOnBDT::get_btag_sf_bin(const LorentzVector& jet) {
    return m_btagging_sf[0]->FindFixBin(jet.Pt());
}

double FWBTagEfficiencyOnBDT::get_btag_sf(uint8_t flav, std::size_t bin) {
    return m_btagging_sf[0]->GetBinContent(bin); 
}

double FWBTagEfficiencyOnBDT::get_btag_sf_error(uint8_t flav, std::size_t bin, const std::string& syst) {
    if ( (syst.find("heavy") != std::string::npos && (flav == 4 || flav == 5)) ||
         (syst.find("light") != std::string::npos && flav == 0) ) {
        return m_btagging_sf_error[flav]->GetBinContent(bin);
    }
    return 0;
}

std::pair<double, double> FWBTagEfficiencyOnBDT::get_range(const TAxis& h) {
    return std::make_pair(
            h.GetBinLowEdge(h.GetFirst()),
            h.GetBinUpEdge(h.GetLast())
            );
}

double FWBTagEfficiencyOnBDT::clip(double var, const std::pair<double, double>& range) {
    if (var < range.first)
        return range.first;

    if (var >= range.second)
        return nextafter(range.second, range.first);

    return var;
}

