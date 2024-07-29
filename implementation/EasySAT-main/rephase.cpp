void Solver::rephase() {
    rephases = 0, threshold *= 0.9, rephase_limit += 8192;
}
