#include <string>
#include <iostream>
#include <memory>

#include <TFile.h>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

class BTagEfficiency {
    public:

        double clip(double var, const std::pair<double, double>& range) {
            if (var < range.first)
                return range.first;

            if (var > range.second)
                return range.second;

            return var;
        }

        double get(const LorentzVector& jet) {
            double pt = clip(jet.Pt(), range_x);
            double eta = clip(jet.Eta(), range_y);
            int64_t binNumber = m_effs->FindBin(pt, eta);
            return m_effs->GetBinContent(binNumber);
        }

        BTagEfficiency() = delete;

        BTagEfficiency(const std::string& file_name) {
                
            std::unique_ptr<TFile> file(TFile::Open(file_name.c_str()));
            if (!file || !file->IsOpen() ){
                std::cerr << "Error: could not open file " << file_name << std::endl;
                exit(1);
            }
                
            std::unique_ptr<TH2> th2(static_cast<TH2*>(file->Get("btagging_eff_on_b")));
            if (!th2 || !th2->InheritsFrom("TH2") ) {
                std::cout << "Error: could not find TH2 \"btagging_eff_on_b\" in file " << file_name << std::endl;
                exit(1);
            }

            range_x = std::make_pair(
                    th2->GetXaxis()->GetBinLowEdge(th2->GetXaxis()->GetFirst()),
                    th2->GetXaxis()->GetBinUpEdge(th2->GetXaxis()->GetLast())
                    );

            range_y = std::make_pair(
                    th2->GetYaxis()->GetBinLowEdge(th2->GetYaxis()->GetFirst()),
                    th2->GetYaxis()->GetBinUpEdge(th2->GetYaxis()->GetLast())
                    );

            th2->SetDirectory(0);
            m_effs = std::move(th2);
        }
        
    private:
        std::pair<double, double> range_x;
        std::pair<double, double> range_y;

        std::unique_ptr<TH2> m_effs;
};
