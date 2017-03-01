#pragma once

#include <vector>
#include <stdexcept>
#include <unordered_map>
#include <chrono>
#include <iostream>

#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float>> LorentzVector;

// From https://stackoverflow.com/questions/35985960/c-why-is-boosthash-combine-the-best-way-to-combine-hash-values
template <class T>
inline void hash_combine(std::size_t& seed, const T& v)
{
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed<<6) + (seed>>2);
}

namespace std {
    template<typename T>
    struct hash<std::vector<T>> {
        std::size_t operator()(const std::vector<T>& k) const {
            std::size_t m_hash = 0;
            for (const auto& v: k)
                hash_combine(m_hash, v);
            return m_hash;
        }
    };
    
    template<>
    struct hash<LorentzVector> {
        std::size_t operator()(const LorentzVector& k) const {
            std::size_t m_hash = 0;
            hash_combine(m_hash, k.Pt());
            hash_combine(m_hash, k.Eta());
            hash_combine(m_hash, k.Phi());
            hash_combine(m_hash, k.E());
            return m_hash;
        }
    };
}

template<typename Evaluator>
class MVAEvaluatorCache {
    public:
        MVAEvaluatorCache(const Evaluator& evaluator): m_evaluator(evaluator) {}
        double evaluate(const std::vector<double>& values);
        void clear();

    private:

        std::unordered_map<std::vector<double>, double> m_cache;
        const Evaluator& m_evaluator;
};

template<typename T> std::size_t get_vector_index(const std::vector<T>& v, const T& x) {
    for (std::size_t i = 0; i < v.size(); i++) {
        if (v[i] == x)
            return i;
    }
    return v.size();
}

double Lerp(double v0, double v1, double t);

std::vector<double> Quantile(const std::vector<double>& inData, const std::vector<double>& probs);
