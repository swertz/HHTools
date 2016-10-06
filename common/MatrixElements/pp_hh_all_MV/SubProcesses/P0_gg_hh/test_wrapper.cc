#include <iostream>
#include <utility>
#include <memory>
#include <vector>
#include <string>

#include "wrapper.h"

int main(int argc, char** argv) {
    WrapperNoTree::pp_hh_noTree test_me("param_card.dat");

    std::pair<std::vector<double>, std::vector<double>> initial = {
        {1.6329036378e+02, +0.0000000000e+00, +0.0000000000e+00, +1.6329036378e+02},
        {1.6622584944e+02, 0.0000000000e+00, -0.0000000000e+00, -1.6622584944e+02}
    };
    std::vector<std::pair<int, std::vector<double>>> final = {
        { 25, {1.6468480455e+02, -8.2163622263e+01, -6.8553031649e+01, +6.7606121871e+00} },
        { 25, {1.6483140867e+02, +8.2163622263e+01, +6.8553031649e+01, -9.6960978395e+00} }
    };

    auto result = test_me.compute(initial, final);

    std::cout << "result: " << result[std::make_pair(21, 21)] << std::endl;
    
    test_me.getParameters()->setParameter("mdl_lambda", 10);
    result = test_me.compute(initial, final);
    std::cout << "result: " << result[std::make_pair(21, 21)] << std::endl;

    return 0;
}
