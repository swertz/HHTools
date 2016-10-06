//==========================================================================
// This file has been automatically generated for C++ Standalone
// MadGraph5_aMC@NLO v. 2.4.0.beta, 2016-04-06
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#ifndef HelAmps_BSM_gg_hh_H
#define HelAmps_BSM_gg_hh_H

#include <cmath> 
#include <complex> 

using namespace std; 

namespace pp_hh_5coup_BSM_gg_hh 
{
void vxxxxx(double p[4], double vmass, int nhel, int nsv, std::complex<double>
    v[6]);

double Sgn(double e, double f); 

void txxxxx(double p[4], double tmass, int nhel, int nst, std::complex<double>
    fi[18]);

void sxxxxx(double p[4], int nss, std::complex<double> sc[3]); 

void ixxxxx(double p[4], double fmass, int nhel, int nsf, std::complex<double>
    fi[6]);

void oxxxxx(double p[4], double fmass, int nhel, int nsf, std::complex<double>
    fo[6]);

void SSS1_0(std::complex<double> S1[], std::complex<double> S2[],
    std::complex<double> S3[], std::complex<double> COUP, std::complex<double>
    & vertex);

}  // end namespace pp_hh_5coup_BSM_gg_hh

#endif  // HelAmps_BSM_gg_hh_H
