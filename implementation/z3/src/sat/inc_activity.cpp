#include "sat/sat_solver.h"
using namespace sat;

void solver::inc_activity(bool_var v) {
    unsigned &act = m_activity[v];
    act += m_activity_inc;
    m_case_split_queue.activity_increased_eh(v);
    if (act > (1 << 24))
        rescale_activity();
}
