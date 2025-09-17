#pragma once

#include <vector>
#include <cmath>
#include <algorithm>
#include <cassert>

using std::abs;

using dvec = std::vector<double>;

namespace mathUtils
{
    // Sign function
    inline int sign(double x) {
        return (x > 0) - (x < 0);
    }

    // Check if vector contains NaN
    inline bool notnan(const dvec& v) {
        for (const auto& val : v) {
            if (!(val > 0) && !(val <= 0)) {
                return false;
            }
        }
        return true;
    }

    // Check if double is not NaN
    inline bool notnan(double v) {
        return (v > 0 || v <= 0);
    }
}