#include <string>
#include <iostream>
#include <memory>

#include <TFile.h>
#include <TEfficiency.h>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

class FWBTagEfficiency {
    public:

        std::pair<double, double> get_range(const TAxis& h) {
            return std::make_pair(
                    h.GetBinLowEdge(h.GetFirst()),
                    h.GetBinUpEdge(h.GetLast())
                    );
        }

        double clip(double var, const std::pair<double, double>& range) {
            if (var < range.first)
                return range.first;

            if (var > range.second)
                return range.second;

            return var;
        }

        double get(const LorentzVector& jet1, const LorentzVector& jet2, size_t njets) {

            /*
             * Some assumptions:
             *  - b-tag efficiencies are binning in pt and eta for all jets
             *  - flavor fractions are binned in jet pt (jet1 pt and jet2 pt)
             */

            uint8_t njets_bin = (njets == 2) ? 2 : 3;

            double weight = 0;

            for (const auto& flav1: flavors) {
                auto jet1_btagging_eff = m_btagging_eff[flav1]->GetEfficiency(m_btagging_eff[flav1]->FindFixBin(jet1.Pt(), std::abs(jet1.Eta())));
                for (const auto& flav2: flavors) {
                    auto jet2_btagging_eff = m_btagging_eff[flav2]->GetEfficiency(m_btagging_eff[flav2]->FindFixBin(jet2.Pt(), std::abs(jet2.Eta())));

                    const auto& fraction_eff = m_fractions[std::make_tuple(flav1, flav2, njets_bin)];
                    auto fraction = fraction_eff->GetEfficiency(fraction_eff->FindFixBin(jet1.Pt(), jet2.Pt()));

                    weight += fraction * jet1_btagging_eff * jet2_btagging_eff;
                }
            }

            return weight;
        }

        FWBTagEfficiency() = delete;

        FWBTagEfficiency(const std::string& btag_efficiencies, const std::string& flavor_fraction) {
                
            std::unique_ptr<TFile> file(TFile::Open(btag_efficiencies.c_str()));
            if (!file || !file->IsOpen() ){
                std::cerr << "Error: could not open file " << btag_efficiencies << std::endl;
                exit(1);
            }

            for (const auto& flav: flavors) {
                std::string name;
                if (flav == 0) {
                    name = "mistagging_eff_on_light";
                } else {
                    name = "btagging_eff_on_" + flavors_to_string[flav];
                }

                std::unique_ptr<TEfficiency> btagging_eff(static_cast<TEfficiency*>(file->Get(name.c_str())));
                if (!btagging_eff) {
                    std::cout << "Error: could not find TEfficiency \"" << name << "\" in file " << btag_efficiencies << std::endl;
                    exit(1);
                }

                btagging_eff->SetDirectory(nullptr);
                m_btagging_eff.emplace(flav, std::move(btagging_eff));
            }

            file.reset(TFile::Open(flavor_fraction.c_str()));
            if (!file || !file->IsOpen() ){
                std::cerr << "Error: could not open file " << flavor_fraction << std::endl;
                exit(1);
            }

            for (const auto& flav1: flavors) {
                for (const auto& flav2: flavors) {
                    for (const auto& njets_bin: njets_binning) {

                        std::string name = flavors_to_string[flav1] + flavors_to_string[flav2] + "_" + njets_to_string[njets_bin] + "_frac";

                        std::unique_ptr<TEfficiency> fraction(static_cast<TEfficiency*>(file->Get(name.c_str())));
                        if (!fraction) {
                            std::cout << "Error: could not find TEfficiency \"" << name << "\" in file " << flavor_fraction << std::endl;
                            exit(1);
                        }

                        std::tuple<uint8_t, uint8_t, uint8_t> key = std::make_tuple(flav1, flav2, njets_bin);
                        fraction->SetDirectory(nullptr);
                        m_fractions.emplace(key, std::move(fraction));
                    }
                }
            }
        }
        
    private:
        std::vector<uint8_t> flavors = {0, 4, 5};
        std::vector<uint8_t> njets_binning = {2, 3};

        std::map<uint8_t, std::string> flavors_to_string = {{0, "l"}, {4, "c"}, {5, "b"}};
        std::map<uint8_t, std::string> njets_to_string = {{2, "2j"}, {3, "3j_and_more"}};

        using key = std::tuple<uint8_t, uint8_t, uint8_t>;
        std::map<key, std::unique_ptr<TEfficiency>> m_fractions;

        std::map<uint8_t, std::unique_ptr<TEfficiency>> m_btagging_eff;
};
