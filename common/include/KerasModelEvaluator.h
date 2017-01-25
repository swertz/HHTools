#pragma once

#include <boost/python.hpp>

#include <iostream>

namespace bp = boost::python;

/**
 * A class acting as a wrapping around a python script, allowing to evaluate a keras model
 */
class KerasModelEvaluator {
    public:
        explicit KerasModelEvaluator(const std::string& keras_model_filename);

        double evaluate(const std::vector<double>& values) const;

        ~KerasModelEvaluator();

    private:
        // Python argv
        char* argv[1];

        bp::object keras_evaluator;
        bp::object keras_method_evaluate;

        void print_python_exception() const;
};
