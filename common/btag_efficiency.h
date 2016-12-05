#include <string>
#include <iostream>
#include <memory>

#include <TFile.h>
#include <TEfficiency.h>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

class BTagEfficiency {
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

        double get(const LorentzVector& jet, int8_t flavor) {
            double pt = clip(jet.Pt(), range_x);
            double eta = clip(jet.Eta(), range_y);

            TEfficiency* effs = nullptr;
            if (flavor == 5)
                effs = m_b_effs.get();
            else if (flavor == 4)
                effs = m_c_effs.get();
            else
                effs = m_l_effs.get();

            int64_t binNumber = effs->FindFixBin(pt, eta);
            return effs->GetEfficiency(binNumber);
        }

        BTagEfficiency() = delete;

        BTagEfficiency(const std::string& file_name) {
                
            std::unique_ptr<TFile> file(TFile::Open(file_name.c_str()));
            if (!file || !file->IsOpen() ){
                std::cerr << "Error: could not open file " << file_name << std::endl;
                exit(1);
            }

            std::unique_ptr<TEfficiency> btagging_b_eff(static_cast<TEfficiency*>(file->Get("btagging_eff_on_b")));
            if (!btagging_b_eff) {
                std::cout << "Error: could not find TEfficiency \"btagging_eff_on_b\" in file " << file_name << std::endl;
                exit(1);
            }

            std::unique_ptr<TEfficiency> btagging_c_eff(static_cast<TEfficiency*>(file->Get("btagging_eff_on_c")));
            std::unique_ptr<TEfficiency> mistagging_l_eff(static_cast<TEfficiency*>(file->Get("mistagging_eff_on_light")));

            btagging_b_eff->SetDirectory(0);
            btagging_c_eff->SetDirectory(0);
            mistagging_l_eff->SetDirectory(0);

            range_x = get_range(*btagging_b_eff->CreateHistogram()->GetXaxis());
            range_y = get_range(*btagging_b_eff->CreateHistogram()->GetYaxis());

            m_b_effs = std::move(btagging_b_eff);
            m_c_effs = std::move(btagging_c_eff);
            m_l_effs = std::move(mistagging_l_eff);
        }
        
    private:
        std::pair<double, double> range_x;
        std::pair<double, double> range_y;

        std::unique_ptr<TEfficiency> m_b_effs;
        std::unique_ptr<TEfficiency> m_c_effs;
        std::unique_ptr<TEfficiency> m_l_effs;
};
