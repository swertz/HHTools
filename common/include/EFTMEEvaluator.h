#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <utility>
#include <iostream>
#include <set>
#include <iomanip>

#include "MatrixElement.h"
#include "MEParameters.h"

#define ZERO_THRESHOLD 1e-15

class EFTMEEvaluatorBase {
    public:
        virtual ~EFTMEEvaluatorBase() {}
        virtual double operator()(const std::map<std::string, double>& params, int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0) = 0;
        virtual double operator()(int op_1, int op_2, int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0, bool reweight_to_sm = false) = 0;
        virtual void computeTerms(int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, std::vector<double>& weights, double alpha_s=0) = 0;
        virtual void printWeights(int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0) = 0;
};

template<typename Process>
class EFTMEEvaluator: public EFTMEEvaluatorBase {
    public:

        EFTMEEvaluator(const std::string& param_card, const std::vector< std::map<std::string, double> >& op_params, std::vector<std::string> _op_names = {}):
            param_card(param_card),
            op_params(op_params),
            me_p1(new Process(param_card)),
            op_names(_op_names)
        {
            for (const auto& op: op_params) {
                for (const auto& par: op)
                    all_params.insert(par.first);
            }
            me_params = me_p1->getParameters();
            if (op_names.size() == 0) {
                for (std::size_t i = 0; i < op_params.size(); i++)
                    op_names.push_back(std::to_string(i));
            }
        }
        
        virtual ~EFTMEEvaluator() {}

        /* Get Matrix Element value for a specific set of parameters
         * - op_params: Set of parameters to evaluate the matrix element with. The parameters with which the EFTMEEvaluator was initialized are not used here.
         * - pid_1, pid_2: initial state PDG IDs
         * - initial: 4-vectors of the initial state
         * - final: PDG IDs and 4-vectors of the final state
         */
        double operator()(const std::map<std::string, double>& params, int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0) override {
            
            auto selected_initial_state = std::make_pair(pid_1, pid_2);

            // Set correct value of alpha_strong
            if (alpha_s > 0) {
                me_params->setParameter("aS", alpha_s);
            }

            // Get parameters before the call and update with what is asked
            reset_params();
            std::map<std::string, double> previous_params;
            for (const auto& param: params) {
                double previous_param = me_params->getParameter(param.first);
                previous_params[param.first] = previous_param;
                me_params->setParameter(param.first, param.second);
            }
 
            double result = me_p1->compute(initial, final)[selected_initial_state];
            
            // Reset parameters to what they were before
            for (const auto& param: previous_params)
                me_params->setParameter(param.first, param.second);
            reset_params();

            if (result == 0)
                std::cout << "Warning: initial state does not contribute!" << std::endl;

            return result;
        }

        /* Get Matrix Element value for contribution of op_1 and op_2
         * - op_1, op_2: operator index desired. `-1` is for the SM, ie:
         *      `(-1, -1)` gives the standard model 
         *      `(0, -1)` and `(-1, 0)` both give the interference of operator 0 with the SM
         *      `(0, 1)` gives the interference of operator 0 with operator 1
         *      `(1, 1)` gives operator 1 squared
         * - pid_1, pid_2: initial state PDG IDs
         * - initial: 4-vectors of the initial state
         * - final: PDG IDs and 4-vectors of the final state
         * - reweight_to_sm: if true, divide the matrix element by the SM value (ie, reweight event with SM as basis)
         * The matrix element is called:
         *  - once for the SM
         *  - twice for SM - op. interferences
         *  - twice for operator squared terms
         *  - 5 times for crossed operator interferences
         */
        double operator()(int op_1, int op_2, int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0, bool reweight_to_sm=false) override {
            
            if (op_1 >= (int) op_params.size() || op_2 >= (int) op_params.size()) {
                std::cout << "Warning: invalid operator IDs " << op_1 << ", " << op_2 << std::endl;
                return 0;
            }

            auto selected_initial_state = std::make_pair(pid_1, pid_2);

            // Set correct value of alpha_strong
            if (alpha_s > 0) {
                me_params->setParameter("aS", alpha_s);
            }

            reset_params();
            double sm_result = me_p1->compute(initial, final)[selected_initial_state];

            if (sm_result == 0) {
                std::cout << "Warning: initial state does not contribute in the SM!" << std::endl;
                return 0;
            }

            double denominator = ( reweight_to_sm ? sm_result : 1 );
            
            ///////// Return SM contribution /////////
            if ( op_1 < 0 && op_2 < 0 ) {
                return sm_result / denominator;
            }
            
            ///////// Return interference /////////
            if (op_1 < 0 && op_2 >= 0)
                std::swap(op_1, op_2);
            if (op_1 >= 0 && op_2 < 0) {
                reset_params();
                set_params(op_params[op_1], 1);
                double f1 = me_p1->compute(initial, final)[selected_initial_state];
                set_params(op_params[op_1], -1);
                double f_1 = me_p1->compute(initial, final)[selected_initial_state];
                return 0.5 * (f1 - f_1) / denominator;
            }

            ///////// Return squared/crossed result /////////
            
            std::vector<std::vector<double>> squared_results(op_params.size());
            for (auto& v: squared_results)
                v.resize(op_params.size());
            std::vector<double> interference_results(op_params.size());
            
            reset_params();
            set_params(op_params[op_1], 1);
            double f10 = me_p1->compute(initial, final)[selected_initial_state];
            set_params(op_params[op_1], -1);
            double f_10 = me_p1->compute(initial, final)[selected_initial_state];

            double I_a = 0.5 * (f10 - f_10);
            double C_a = 0.5 * (f10 + f_10) - sm_result;
            
            // Only squared result: we have what we need
            if (op_1 == op_2)
                return C_a / denominator;

            // Crossed term: some more work needed
            reset_params();
            set_params(op_params[op_2], 1);
            double f01 = me_p1->compute(initial, final)[selected_initial_state];
            set_params(op_params[op_2], -1);
            double f0_1 = me_p1->compute(initial, final)[selected_initial_state];

            reset_params();
            add_params(op_params[op_1], 1);
            add_params(op_params[op_2], 1);
            double f11 = me_p1->compute(initial, final)[selected_initial_state];

            double I_b = 0.5 * (f01 - f0_1);
            double C_b = 0.5 * (f01 + f0_1) - sm_result;
            double I_ab = f11 - sm_result - I_a - I_b - C_a - C_b;

            return I_ab / denominator;
        }

        /*
         * Compute weights for all terms and fill them into vector ´weights`
         * - pid_1, pid_2: initial state PDG IDs
         * - initial: 4-vectors of the initial state
         * - final: PDG IDs and 4-vectors of the final state
         * - weights: Output vector containing all the weights, in that order (operators 1...n):
         * SM -- interf. ( 1 ... n ) -- squared ( 1 ... n )
         *                                      ( .     . )
         *                                      ( n     . )
         * corresponds to index in vector:
         * 0               1 ... n+1              n+2  2n+3 2n+4 ...
         *                                        2n+3 n+3  2n+5 ...
         *                                        2n+4 2n+5 n+4  ...
         *                                        .    .    .    ...
         *                                        .    .    .    ...  2n+2
         * The matrix element is called in total 1 + n(3+n)/2 times
         */
        void computeTerms(int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, std::vector<double> & weights, double alpha_s=0) override {
            std::size_t n = op_params.size();

            if (weights.size() != 1 + n * (3 + n) / 2) {
                std::cout << "Warning: invalid vector size!" << std::endl;
                return;
            }
            
            // Set correct value of alpha_strong
            if (alpha_s > 0) {
                me_params->setParameter("aS", alpha_s);
            }

            auto selected_initial_state = std::make_pair(pid_1, pid_2);

            reset_params();
            double sm_result = me_p1->compute(initial, final)[selected_initial_state];

            if (sm_result == 0) {
                std::cout << "Warning: initial state does not contribute in the SM!" << std::endl;
                return;
            }

            std::vector<double> single_evals_pos(n); // holds terms of type f(1,0,...)
            std::vector<double> single_evals_neg(n); // holds terms of type f(-1,0,...)
            std::vector<double> double_evals(n * (n - 1) / 2); // holds terms of type f(1,0,...,1,0,...)

            // First evaluate all terms
            int count = 0;
            for (int i = 0; i < n; i++) {
                reset_params();
                
                set_params(op_params[i], 1);
                single_evals_pos[i] = me_p1->compute(initial, final)[selected_initial_state];
                set_params(op_params[i], -1);
                single_evals_neg[i] = me_p1->compute(initial, final)[selected_initial_state];
            
                for (int j = 0; j < i; j++) {
                    reset_params();
                    add_params(op_params[i], 1);
                    add_params(op_params[j], 1);

                    double_evals[count] = me_p1->compute(initial, final)[selected_initial_state];
                    count++;
                }
            }

            // Then compute weights

            // SM
            weights[0] = sm_result;

            // Interferences: using f(1,0...) - f(-1,0,...)
            for (int i = 0; i < n; i++)
                weights[i + 1] = 0.5 * (single_evals_pos[i] - single_evals_neg[i]);

            // Crossed terms
            count = 0;
            for (int i = 0; i < n; i++) {
                double C_i = 0.5 * (single_evals_pos[i] + single_evals_neg[i]) - sm_result;
                //std::cout << "Setting weight for op " << op_names[i] << ", " << op_names[i] << " at index " << n+1+i << std::endl;
                weights.at(n + 1 + i) = C_i;
 
                for (int j = 0; j < i; j++) {
                    double I_i = 0.5 * (single_evals_pos[i] - single_evals_neg[i]);
                    double I_j = 0.5 * (single_evals_pos[j] - single_evals_neg[j]);
                    double C_j = 0.5 * (single_evals_pos[j] + single_evals_neg[j]) - sm_result;
                    double I_ij = double_evals.at(count) - sm_result - I_i - I_j - C_i - C_j;
                    //std::cout << "Setting weight for op " << op_names[i] << ", " << op_names[j] << " at index " << 2*n+1+count << std::endl;
                    weights.at(2*n + 1 + count) = I_ij;
                    count++;
                }
            }
        }

        /* Print all contributions (interferences and crossed terms), reweighted to the SM, in a nice formatted output
         * - pid_1, pid_2: initial state PDG IDs
         * - initial: 4-vectors of the initial state
         * - final: PDG IDs and 4-vectors of the final state
         */
        void printWeights(int pid_1, int pid_2, std::pair< std::vector<double>, std::vector<double> >& initial, std::vector< std::pair<int, std::vector<double> > >& final, double alpha_s=0) override {
            auto selected_initial_state = std::make_pair(pid_1, pid_2);

            // Set correct value of alpha_strong
            if (alpha_s > 0) {
                me_params->setParameter("aS", alpha_s);
            }

            double sm_result = operator()(-1, -1, pid_1, pid_2, initial, final);
            
            if (sm_result == 0) {
                return;
            }

            std::vector<std::vector<double>> squared_results(op_params.size());
            for (auto& v: squared_results)
                v.resize(op_params.size());
            std::vector<double> interference_results(op_params.size());

            for (std::size_t i = 0; i < op_params.size(); i++) {
                double interf = operator()(i, -1, pid_1, pid_2, initial, final);
                if (fabs(interf)/sm_result <= ZERO_THRESHOLD)
                    interf = 0;
                interference_results[i] = interf;

                for (std::size_t j = i; j < op_params.size(); j++) {
                    double squared = operator()(i, j, pid_1, pid_2, initial, final);

                    if (fabs(squared)/sm_result <= ZERO_THRESHOLD)
                        squared = 0;
                    
                    squared_results[i][j] = squared;
                }
            }
        
            std::cout << "SM result: " << sm_result << std::endl << std::endl;
            
            std::cout << "Interference SM - operators: " << std::endl << std::setw(5) << " ";
            for (std::size_t i = 0; i < op_params.size(); i++)
                std::cout << std::setw(12) << op_names[i];
            std::cout << std::endl  << std::setw(5) << " " << std::scientific << std::setprecision(3);
            for (std::size_t i = 0; i < op_params.size(); i++)
                std::cout << std::setw(12) << interference_results[i]/sm_result;
            std::cout << std::endl << std::endl;
            
            std::cout << "Interference operator - operator: " << std::endl << std::setw(5) << " ";
            for (std::size_t i = 0; i < op_params.size(); i++)
                std::cout << std::setw(12) << op_names[i];
            std::cout << std::endl;
            for (std::size_t i = 0; i < op_params.size(); i++) {
                std::cout << std::setw(5) << op_names[i];
                for (std::size_t j = 0; j < i; j++)
                    std::cout << std::setw(12) << " ";
                for (std::size_t j = i; j < op_params.size(); j++)
                    std::cout << std::setw(12) << squared_results[i][j]/sm_result;
                std::cout << std::endl;
            }
            std::cout << std::endl;
        }
            
    private:
   
        // Reset all EFT couplings considered to zero
        void reset_params() {
            for (const std::string& param: all_params)
                me_params->setParameter(param, 0);
        }

        // Set all EFT couplings declared in 'params' to their default value times the 'factor'
        void set_params(std::map<std::string, double> params, double factor) {
            for (const auto& param: params) {
                me_params->setParameter(param.first, factor*param.second);
            }
        }

        // Add to all EFT couplings declared in 'params' their default value times the 'factor'
        void add_params(std::map<std::string, double> params, double factor) {
            for (const auto& param: params) {
                double current_param = me_params->getParameter(param.first);
                me_params->setParameter(param.first, current_param + factor*param.second);
            }
        }
    
        const std::string param_card;
        const std::vector< std::map<std::string, double> > op_params;
        std::shared_ptr<momemta::MatrixElement> me_p1;
        std::shared_ptr<momemta::MEParameters> me_params;
        std::set<std::string> all_params;
        std::vector<std::string> op_names;
};
