#include <string>
#include <iostream>
#include <memory>

#include <TFile.h>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

class DYReweighter {
    public:

        double getWeight(const LorentzVector& lep1, const LorentzVector& lep2) {

            int64_t binNumber = m_weights->FindBin(lep1.Pt(), lep2.Pt());
            return m_weights->GetBinContent(binNumber);
        }

        DYReweighter() = delete;

        DYReweighter(const std::string& file_name) {
                
            std::unique_ptr<TFile> file(TFile::Open(file_name.c_str()));
            if (!file || !file->IsOpen() ){
                std::cerr << "Error: could not open file " << file_name << std::endl;
                exit(1);
            }
                
            std::unique_ptr<TH2> th2(static_cast<TH2*>(file->Get("ratio")));
            if (!th2 || !th2->InheritsFrom("TH2") ) {
                std::cout << "Error: could not find TH2 \"ratio\" in file " << file_name << std::endl;
                exit(1);
            }

            th2->SetDirectory(0);
            m_weights = std::move(th2);
        }
        
    private:
        std::unique_ptr<TH2> m_weights;
};
