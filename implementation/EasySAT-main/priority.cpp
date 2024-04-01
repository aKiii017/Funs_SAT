#include "EasySAT.hpp"
#include <fstream>

void Solver::priority(int var, double coeff) {
public:
        void priority_v1(int var, double coeff) {
            activity[var] = std::min(activity[var] + var_inc * coeff, 1e100);
            if (vsids.inHeap(var)) vsids.update(var);
        }
}
