#include "KerasModelEvaluator.h"

#include <numpy/ndarrayobject.h>

KerasModelEvaluator::KerasModelEvaluator(const std::string& keras_model_filename) {
    argv[0] = (char*) malloc(7);
    strcpy(argv[0], "python");

    Py_Initialize();
    PySys_SetArgv(1, argv);
    import_array();

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

        predictions = self.model.predict_on_batch(values)
        return predictions
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

KerasModelEvaluator::~KerasModelEvaluator() {
    free(argv[0]);
}

double KerasModelEvaluator::evaluate(const std::vector<double>& values) const {
    try {
        npy_intp shape[] = {1, (npy_intp) values.size()}; // array size
        PyObject *obj = PyArray_SimpleNewFromData(2, shape, NPY_DOUBLE, const_cast<double*>(values.data()));

        bp::handle<> py_array(obj);
        bp::object result = keras_method_evaluate(py_array);

        PyArrayObject* np_result = reinterpret_cast<PyArrayObject*>(result.ptr());
        float* data = static_cast<float*>(PyArray_DATA(np_result));
        return data[0];

    } catch(...) {
        print_python_exception();
        throw;
    }
}

void KerasModelEvaluator::print_python_exception() const {
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
