#include "LWTNNEvaluator.h"

#include <lwtnn/parse_json.hh>

#include <fstream>

LWTNNEvaluator::LWTNNEvaluator(const std::string& lwtnn_model_filename, const std::vector<std::string>& inputs_name): inputs_name(inputs_name) {

    std::cout << "Initializing LWTNN evaluator using " << lwtnn_model_filename << std::endl;

    std::ifstream config_file(lwtnn_model_filename);
    auto config = lwt::parse_json(config_file);

    nn.reset(new lwt::LightweightNeuralNetwork(config.inputs, config.layers, config.outputs));

    for (const auto& name: inputs_name) {
        inputs.emplace(name, 0);
    }

    std::cout << "Done." << std::endl;
}

LWTNNEvaluator::~LWTNNEvaluator() {
}

double LWTNNEvaluator::evaluate(const std::vector<double>& values) const {
    size_t index = 0;
    for (const auto& name: inputs_name) {
        inputs[name] = values[index++];
    }

    return nn->compute(inputs)["signal"];
}
