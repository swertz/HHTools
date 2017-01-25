#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <cassert>

#include <TMVA/Reader.h>


class TMVAEvaluator {
    public:
        TMVAEvaluator(const std::string& xmlPath, const std::vector<std::string>& variables);

        double evaluate(const std::vector<double>& values) const;

    private:

        mutable std::vector<float> m_variables;
        std::shared_ptr<TMVA::Reader> m_reader;
};
