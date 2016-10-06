//==========================================================================
// This file has been automatically generated for C++ Standalone
// MadGraph5_aMC@NLO v. 2.5.0.alpha, 2016-08-28
// By the MadGraph5_aMC@NLO Development Team
// Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
//==========================================================================

#ifndef HelAmps_modTEFT_H_H
#define HelAmps_modTEFT_H_H

#include <cmath> 
#include <complex> 

using namespace std; 

namespace pp_hh_tree_MV_standalone_modTEFT_H 
{
void txxxxx(double p[4], double tmass, int nhel, int nst, std::complex<double>
    fi[18]);

void vxxxxx(double p[4], double vmass, int nhel, int nsv, std::complex<double>
    v[6]);

double Sgn(double e, double f); 

void ixxxxx(double p[4], double fmass, int nhel, int nsf, std::complex<double>
    fi[6]);

void sxxxxx(double p[4], int nss, std::complex<double> sc[3]); 

void oxxxxx(double p[4], double fmass, int nhel, int nsf, std::complex<double>
    fo[6]);

void VVS20_3(std::complex<double> V1[], std::complex<double> V2[],
    std::complex<double> COUP, double M3, double W3, std::complex<double> S3[]);

void VVSS26_0(std::complex<double> V1[], std::complex<double> V2[],
    std::complex<double> S3[], std::complex<double> S4[], std::complex<double>
    COUP, std::complex<double> & vertex);

void SSS2_0(std::complex<double> S1[], std::complex<double> S2[],
    std::complex<double> S3[], std::complex<double> COUP, std::complex<double>
    & vertex);

}  // end namespace pp_hh_tree_MV_standalone_modTEFT_H

#endif  // HelAmps_modTEFT_H_H
