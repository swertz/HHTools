#pragma once

#include <boost/python.hpp>

#include <iostream>

namespace bp = boost::python;

/**
 * A class acting as a wrapping around a python script, allowing to evaluate a keras model
 */
class KerasModelEvaluator {
    public:
        explicit KerasModelEvaluator(const std::string& keras_model_filename) {
            argv[0] = (char*) malloc(7);
            strcpy(argv[0], "python");

            Py_Initialize();
            PySys_SetArgv(1, argv);

            const std::string python_wrapper = R"(

# Set number of available cores to 1
import os
os.environ['OMP_NUM_THREADS'] = '1'

import sys

_stderr = sys.stderr
sys.stderr = sys.stdout
import keras
sys.stderr.flush()
sys.stderr = _stderr
del _stderr

import numpy as np

class KerasModelEvaluator(object):

    def __init__(self, filename):
        print("Loading Keras model from %r" % filename)
        self.model = keras.models.load_model(filename)

    def evaluate_single_event(self, values):
        """
        Evaluate the model on a single event

        Parameters:
          values: list of inputs

        Returns:
          The model output
        """

        values = np.array(values).reshape(1, len(values))
        predictions = self.model.predict(values)
        return predictions[0][0].astype(np.float64)
)";

            try {
                std::cout << "Initializing Keras model evaluator..." << std::endl;
                bp::object main = bp::import("__main__");
                bp::object global(main.attr("__dict__"));

                // Execute the script
                bp::object result = bp::exec(python_wrapper.c_str(), global, global);

                // The python script must define a class named 'KerasModelEvaluator'
                bp::object clazz = global["KerasModelEvaluator"];

                // Create a new instance of the class
                keras_evaluator = clazz(keras_model_filename);
                keras_method_evaluate = keras_evaluator.attr("evaluate_single_event");
                std::cout << "All done." << std::endl;
            } catch(...) {
                print_python_exception();
                throw;
            }
        }

        double evaluate(const std::vector<double>& values) const {
            try {
                bp::list py_values;
                for (const auto& v: values)
                    py_values.append(v);

                return bp::extract<double>(keras_method_evaluate(py_values))();
            } catch(...) {
                print_python_exception();
                throw;
            }
        }

        ~KerasModelEvaluator() {
            free(argv[0]);
        }

    private:
        // Python argv
        char* argv[1];

        bp::object keras_evaluator;
        bp::object keras_method_evaluate;

        void print_python_exception() const {
            PyObject *ptype, *pvalue, *ptraceback;
            PyErr_Fetch(&ptype, &pvalue, &ptraceback);

            std::cout << "Python exception - ";

            if (pvalue) {
                std::cout << PyString_AsString(pvalue);
            } else {
                std::cout << " <exception message unavailable>";
            }

            std::cout << std::endl;
            std::cout << "Stack trace: " << std::endl;

            if (ptraceback) {
                bp::object tb(bp::import("traceback"));
                bp::object fmt_tb(tb.attr("format_tb"));
                bp::object tb_list(fmt_tb(bp::handle<>(ptraceback)));
                bp::object tb_str(bp::str("\n").join(tb_list));
                bp::extract<std::string> returned(tb_str);
                if(returned.check())
                    std::cout << returned();
                else
                    std::cout << "Unparseable Python traceback";
            } else {
                std::cout << "No stack trace :(";
            }

            std::cout << std::endl;
        }
};

template <typename Key, typename Evaluator>
class KerasModelEvaluatorCache {
    public:
        explicit KerasModelEvaluatorCache(const Evaluator& evaluator): m_evaluator(evaluator) {}

        double evaluate(const Key& key, const std::vector<double>& values) {
            auto it = m_evaluation_cache.find(key);
            if (it == m_evaluation_cache.end()) {
                double result = m_evaluator.evaluate(values);
                m_evaluation_cache.emplace(key, result);

                return result;
            } else {
                return it->second;
            }
        }

        void clear() {
            m_evaluation_cache.clear();
        }

    private:
        std::unordered_map<Key, double> m_evaluation_cache;
        const Evaluator& m_evaluator;
};
