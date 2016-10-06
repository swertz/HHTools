#pragma once

#include "MEParameters.h"
#include "MatrixElement.h"

namespace WrapperOphiGOps {

    class ParametersWrapper: public momemta::MEParameters {
        public:
            ParametersWrapper(const std::string& param_card);
            virtual ~ParametersWrapper() {}

            virtual void cacheParameters() override;
            
            virtual void cacheCouplings() override;

            virtual void updateParameters() override {}
            virtual void updateCouplings() override {}
    };

    class pp_hh_OphiG_ops: public momemta::MatrixElement {
        public:
            pp_hh_OphiG_ops(const std::string& param_card);
            virtual ~pp_hh_OphiG_ops() {}

            virtual Result compute(
                    const std::pair<std::vector<double>, std::vector<double>>& initialMomenta,
                    const std::vector<std::pair<int, std::vector<double>>>& finalState
                    );

            virtual std::shared_ptr<momemta::MEParameters> getParameters();

        private:
            std::shared_ptr<ParametersWrapper> params;
    };

}
