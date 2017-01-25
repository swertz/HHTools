#include <string>
#include <map>
#include <iostream>
#include <memory>

#include <TFile.h>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

class BenchmarkReweighter {
    public:

        double getWeight(const uint32_t bm, const LorentzVector& h1, const LorentzVector& h2) {
            TH2* this_th = m_weights.at(bm);

            double m_hh = (h1 + h2).M();
            double cos_theta_star = getCosThetaStar_CS(h1, h2);

            int64_t binNumber = this_th->FindBin(m_hh, cos_theta_star);

            return this_th->GetBinContent(binNumber);
        }

        double getWeight(const uint32_t bm, const double m_hh, const double cos_theta_star) {
            TH2* this_th = m_weights.at(bm);

            int64_t binNumber = this_th->FindBin(m_hh, cos_theta_star);

            return this_th->GetBinContent(binNumber);
        }

        double getCosThetaStar_CS(const LorentzVector& h1, const LorentzVector& h2) {
            double ebeam = 6500;

            LorentzVector p1, p2;
            p1.SetPxPyPzE(0, 0,  ebeam, ebeam);
            p2.SetPxPyPzE(0, 0, -ebeam, ebeam);

            LorentzVector hh = h1 + h2;
            ROOT::Math::Boost boost(-hh.X() / hh.T(), -hh.Y() / hh.T(), -hh.Z() / hh.T());
            p1 = boost(p1);
            p2 = boost(p2);
            LorentzVector newh1 = boost(h1);
            ROOT::Math::DisplacementVector3D<ROOT::Math::Cartesian3D<double>> CSaxis(p1.Vect().Unit() - p2.Vect().Unit());

            return cos(ROOT::Math::VectorUtil::Angle(CSaxis.Unit(), newh1.Vect().Unit()));
        }

        BenchmarkReweighter() = delete;

        BenchmarkReweighter(std::string baseDirPath, uint32_t nStart, uint32_t nStop, bool manyFiles, std::string nameTemplate, std::string templateIdx) {
            if (manyFiles) {
                
                for (uint32_t bm = nStart; bm <= nStop; bm++) {
                    std::string thisFileName = nameTemplate;
                    std::size_t pos = thisFileName.find(templateIdx);
                    thisFileName.replace(pos, templateIdx.length(), std::to_string(bm));
                    std::string path = baseDirPath + "/" + thisFileName;
                    TFile *file = TFile::Open(path.c_str());
                    if (!file || !file->IsOpen() ){
                        std::cout << "Warning: could not open file " << path << std::endl;
                        continue;
                    }
                    
                    TH2 *th2 = static_cast<TH2*>(file->Get("weights_unfolded"));
                    if (!th2 || !th2->InheritsFrom("TH2") ) {
                        std::cout << "Warning: could not find TH2 \"weights\" in file " << path << std::endl;
                        continue;
                    }
                    th2->SetDirectory(0);
                    m_weights[bm] = th2;

                    std::cout << "Added weights histogram for benchmark nr. " << bm << std::endl;
                }
            
            } else {
                
                TFile *file = TFile::Open(baseDirPath.c_str());
                if (!file || !file->IsOpen() ){
                    std::cerr << "Error: could not open file " << baseDirPath << std::endl;
                    exit(1);
                }
                
                for (uint32_t bm = nStart; bm <= nStop; bm++) {
                    std::string thisName = nameTemplate;
                    std::size_t pos = thisName.find(templateIdx);
                    thisName.replace(pos, templateIdx.length(), std::to_string(bm));
                    TH2 *th2 = static_cast<TH2*>(file->Get(thisName.c_str()));
                    if (!th2 || !th2->InheritsFrom("TH2") ) {
                        std::cout << "Warning: could not find TH2 \"weights\" in file " << baseDirPath << std::endl;
                        continue;
                    }
                    th2->SetDirectory(0);
                    m_weights[bm] = th2;

                    std::cout << "Added weights histogram for benchmark nr. " << bm << std::endl;
                }

                file->Close();
            }
        }
        
        ~BenchmarkReweighter() {
            for(auto& entry: m_weights)
                delete entry.second;
        }

    private:
        std::map<uint32_t, TH2*> m_weights;
};

static BenchmarkReweighter& getBenchmarkReweighter(std::string baseDirPath = "", uint32_t nStart = 0, uint32_t nStop = 0, bool manyFiles = true, std::string nameTemplate = "", std::string templateIdx = "") {
    static shared_ptr<BenchmarkReweighter> m_reweighter = std::make_shared<BenchmarkReweighter>(baseDirPath, nStart, nStop, manyFiles, nameTemplate, templateIdx);
    return *m_reweighter; 
}
