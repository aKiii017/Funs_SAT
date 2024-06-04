void rephase(int& rephases, int& threshold, int& rephase_limit) {
    const int conflicts_max = 5000;
    const double threshold_default = 0.9;
    const double threshold_min = 0.05;
    const int rephase_limit_increment_base = 8192;
    const double threshold_decrease_factor = 0.8;
    const int rephase_limit_increment_factor1 = 2;
    const int rephase_limit_increment_factor2 = 4;
    const int rephase_limit_reset_factor = 5000;

    int increment_factor = rephase_limit_increment_base;

    if (rephases > conflicts_max) {
        increment_factor = (rephases > 2000) ? rephase_limit_increment_base * rephase_limit_increment_factor1 :
                    rephase_limit_increment_base * rephase_limit_increment_factor2;
        threshold *= threshold_decrease_factor;
    }
    rephase_limit += increment_factor;

    if (threshold < threshold_min) {
        rephases = 0;
        threshold = threshold_default;
        rephase_limit = rephase_limit_reset_factor;
    }
}
