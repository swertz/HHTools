#pragma once

#include <lwtnn/LightweightNeuralNetwork.hh>

#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>

/**
 * A class acting as a wrapping around a python script, allowing to evaluate a keras model
 */
class LWTNNEvaluator {
    public:
        explicit LWTNNEvaluator(const std::string& lwtnn_model_filename, const std::vector<std::string>& inputs_name);

        double evaluate(const std::vector<double>& values) const;

        ~LWTNNEvaluator();

    private:
        // Python argv
        char* argv[1];

        std::unique_ptr<lwt::LightweightNeuralNetwork> nn;
        std::vector<std::string> inputs_name;

        mutable std::map<std::string, double> inputs;
};
