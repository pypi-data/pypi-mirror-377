/**
 * @file qss_integrator.cpp
 * @brief Implementation of the Quasi-Steady-State (QSS) integrator for stiff ODEs
 * 
 * This implementation is based on the CHEMEQ2 algorithm and the QSS method described in:
 * Mott, D., Oran, E., & van Leer, B. (2000). A Quasi-Steady-State Solver for the 
 * Stiff Ordinary Differential Equations of Reaction Kinetics. Journal of Computational 
 * Physics, 164(2), 407-428.
 * 
 * The QSS method splits ODEs into production (q) and destruction (d) terms:
 * dy/dt = q(y) - d(y)
 * where q represents production rates and d represents destruction rates.
 */

#include "qss_integrator.h"
#include <iostream>
#include <algorithm>

using std::abs;
using mathUtils::sign;

QssIntegrator::QssIntegrator()
    : ode_(nullptr)
{
    N = 0;
    epsmax = 20;
    epsmin = 1e-2;
    dtmin = 1e-15;
    dtmax = 1e-6;
    itermax = 2;
    tfd = 1.000008;
    abstol = 1e-8;
    stabilityCheck = true;
    firstStep = true;
    dt = 0;
    ts = 0;
    gcount = 0;
    rcount = 0;
    tn = 0;
}

void QssIntegrator::setOde(QssOde* ode)
{
    ode_ = ode;
}

void QssIntegrator::initialize(size_t N_)
{
    N = N_;
    y.resize(N);
    q.resize(N);
    d.resize(N);
    rtaus.resize(N);
    y1.resize(N);
    ys.resize(N);
    rtau.resize(N);
    qs.resize(N);
    ymin.assign(N, 1e-20);
    enforce_ymin.assign(N, 1.0);
    ym1.resize(N);
    ym2.resize(N);
    scratch.resize(N);
}

void QssIntegrator::setState(const dvec& yIn, double tstart_)
{
    assert(yIn.size() == N);
    assert(mathUtils::notnan(yIn));

    // Store and limit to 'ymin' the initial values.
    for (size_t i = 0; i < N; i++) {
        if (enforce_ymin[i]) {
            y[i] = std::max(yIn[i], ymin[i]);
        } else {
            y[i] = yIn[i];
        }
    }

    gcount = 0;
    rcount = 0;
    tstart = tstart_;
    tn = 0.0;
    firstStep = true;
}

void QssIntegrator::getInitialStepSize(double tf)
{
    firstStep = false;
    double scratch_value = 1.0e-25;

    for (size_t i = 0; i < N; i++) {
        if (abs(y[i]) > abstol) {
            const double absq = abs(q[i]);
            const double scr2 = abs(1/y[i]) * sign(0.1*epsmin*absq - d[i]);
            const double scr1 = scr2 * d[i];
            scratch_value = std::max(std::max(scr1, -abs(absq-d[i])*scr2), scratch_value);
        }
    }

    const double sqreps = 0.5;
    dt = std::min(sqreps/scratch_value, tf);
    dt = std::min(dt, dtmax);
}

int QssIntegrator::integrateToTime(double tf)
{
    while (tfd*tn < tf) {
        int ret = integrateOneStep(tf);
        if (ret) {
            return ret;
        }
    }
    return 0;
}

int QssIntegrator::integrateOneStep(double tf) {
    // Evaluate the derivatives at the initial state.
    assert(mathUtils::notnan(y));
    ode_->odefun(tn + tstart, y, q, d);
    assert(mathUtils::notnan(q));
    assert(mathUtils::notnan(d));
    gcount += 1;

    if (firstStep) {
        getInitialStepSize(tf);
    }

    // Store starting values
    ts = tn;
    for (size_t i = 0; i < N; i++) {
        rtau[i] = enforce_ymin[i] ? dt * d[i] / y[i] : 0.0;
    }
    qs = q;
    ys = y;
    rtaus = rtau;

    // Repeat integration until a successful timestep has been taken
    while (true) {
        // Find the predictor terms.
        for (size_t i = 0; i < N; i++) {
            double denom = 1.0 + rtau[i] * (180+rtau[i]*(60+rtau[i]*(11+rtau[i]))) /
                                          (360 + rtau[i]*(60 + rtau[i]*(12 + rtau[i])));
            scratch[i] = (q[i] - d[i]) / denom;
        }

        double eps = 1e-10;
        for (int iter = 0; iter < itermax; iter++) {
            // limit decreasing functions to their minimum values.
            if (stabilityCheck) {
                ym2 = ym1;
                ym1 = y;
            }

            for (size_t i = 0; i < N; i++) {
                double new_val = ys[i] + dt*scratch[i];
                y[i] = std::max(new_val, ymin[i]);
            }

            if (iter == 0) {
                tn = ts + dt;
                y1 = y;
            }

            // Evaluate the derivatives for the corrector.
            assert(mathUtils::notnan(y));
            ode_->odefun(tn + tstart, y, q, d, true);
            assert(mathUtils::notnan(q));
            assert(mathUtils::notnan(d));
            gcount += 1;

            dvec rtaub(N);
            for (size_t i = 0; i < N; i++) {
                rtaub[i] = enforce_ymin[i] ? 0.5 * (rtaus[i] + dt * d[i] / y[i]) : 0.0;
            }
            
            dvec alpha(N);
            for (size_t i = 0; i < N; i++) {
                alpha[i] = (180.+rtaub[i]*(60.+rtaub[i]*(11.+rtaub[i]))) /
                          (360. + rtaub[i]*(60. + rtaub[i]*(12. + rtaub[i])));
            }
            
            for (size_t i = 0; i < N; i++) {
                scratch[i] = (qs[i]*(1.0 - alpha[i]) + q[i]*alpha[i] - ys[i]*rtaub[i]/dt) / 
                            (1.0 + alpha[i]*rtaub[i]);
            }
        }

        // Calculate new f, check for convergence
        eps = 0.0;  // Initialize convergence error
        for (size_t i = 0; i < N; i++) {
            double new_y = ys[i] + dt*scratch[i];
            if (enforce_ymin[i]) {
                new_y = std::max(new_y, ymin[i]);
            }
            double error = abs(new_y - y1[i]);
            y[i] = std::max(new_y, ymin[i]);

            if (abs(y[i]) > abstol && 0.25*(ys[i] + y[i]) > ymin[i]) {
               error = error/y[i];
               eps = std::max(.5*(error+ std::min(abs(q[i]-d[i])/(q[i]+d[i]+1e-30), error)),eps);
            }
        }
        assert(mathUtils::notnan(y));

        if (stabilityCheck) {
            ym2 = ym1;
            ym1 = y;
        }

        eps /= epsmin;

        if (dt <= dtmin + 1e-16*tn) {
            std::cerr << "QssIntegrator failed: timestep too small: dt = " << dt 
                      << ", tn = " << tn << ", dtmin = " << dtmin << std::endl;
            return -1;
        }

        // Stability check
        double stab = 0;
        if (stabilityCheck && itermax >= 3) {
            stab = 0.01;
            for (size_t i = 0; i < N; i++) {
                if (abs(y[i]) > abstol) {
                    stab = std::max(stab, abs(y[i]-ym1[i])/(abs(ym1[i]-ym2[i])+1e-20*y[i]));
                }
            }
        }

        if (eps <= epsmax && stab <= 1.0) {
            if (tf <= tn*tfd) {
                return 0;
            }
        } else {
            tn = ts;
        }

        // Perform stepsize modifications.
        double rteps = 0.5*(eps + 1.0);
        rteps = 0.5*(rteps + eps/rteps);
        rteps = 0.5*(rteps + eps/rteps);

        double dto = dt;
        dt = std::min(dt*(1.0/rteps + 0.005), tfd*(tf - tn));
        dt = std::min(dt, dtmax);
        if (stabilityCheck) {
            dt = std::min(dt, dto/(stab+.001));
        }

        if (eps > epsmax || stab > 1) {
            rcount += 1;
            for (size_t i = 0; i < N; i++) {
                rtaus[i] *= dt/dto;
            }
        } else {
            return 0;
        }
    }
}