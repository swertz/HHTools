#include <algorithm>

#include "utils.h"

double Lerp(double v0, double v1, double t) {
    return (1 - t) * v0 + t * v1;
}

std::vector<double> Quantile(const std::vector<double>& inData, const std::vector<double>& probs) {
    if (inData.size() <= 2 || probs.empty()) {
        throw std::runtime_error("Invalid input");
    }

    std::vector<double> data = inData;
    std::sort(data.begin(), data.end());
    std::vector<double> quantiles;

    for (size_t i = 0; i < probs.size(); ++i) {
        double center = Lerp(-0.5, data.size() - 0.5, probs[i]);

        size_t left = std::max(int64_t(std::floor(center)), int64_t(0));
        size_t right = std::min(int64_t(std::ceil(center)), int64_t(data.size() - 1));

        double datLeft = data.at(left);
        double datRight = data.at(right);

        double quantile = Lerp(datLeft, datRight, center - left);

        quantiles.push_back(quantile);
    }

    return quantiles;
}

