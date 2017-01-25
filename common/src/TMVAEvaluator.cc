#include "TMVAEvaluator.h"

TMVAEvaluator::TMVAEvaluator(const std::string& xmlPath, const std::vector<std::string>& variables) {
    std::cout << "Initializing TMVAEvaluator for xml file " << xmlPath << std::endl;

    m_reader = std::make_shared<TMVA::Reader>("Silent=1");
    
    m_variables.resize(variables.size());

    for (std::size_t i = 0; i < m_variables.size(); i++)
        m_reader->AddVariable(variables[i].c_str(), &m_variables[i]);

    m_reader->BookMVA("MVA", xmlPath.c_str());
}

double TMVAEvaluator::evaluate(const std::vector<double>& values) const {
    assert(values.size() == m_variables.size());

    for (std::size_t i = 0; i < m_variables.size(); i++)
        m_variables[i] = values[i];

    return m_reader->EvaluateMVA("MVA");
}
