#include <string>
#include <vector>
#include <memory>
#include <map>
#include <TMVA/Reader.h>

// Does not support spectator variables yet
float evaluateMVA(const std::string & xmlPath, const std::vector<std::pair<std::string, float>> & variables) {
    static std::map<std::string, std::shared_ptr<TMVA::Reader>> readers;
    static std::map<std::string, std::vector<float>> local_variables;
    
    auto readers_it = readers.find(xmlPath);
    if (readers_it == readers.end()) {
        std::shared_ptr<TMVA::Reader> reader(new TMVA::Reader("Silent=1"));
        auto & local_mva_variables = local_variables[xmlPath];
        local_mva_variables.resize(variables.size());
        for (size_t i = 0; i < variables.size(); i++) {
            reader->AddVariable(variables[i].first.c_str(), & local_mva_variables[i]);
        }
        reader->BookMVA("MVA", xmlPath.c_str());
        readers.emplace(xmlPath, reader);
        readers_it = readers.find(xmlPath);
    }

    for (size_t i = 0; i < variables.size(); i++) {
        local_variables[xmlPath][i] = variables[i].second;
    }

    return readers_it->second->EvaluateMVA("MVA");
}
