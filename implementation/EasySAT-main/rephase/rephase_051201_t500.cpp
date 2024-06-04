void rephase(int& rephases, int& threshold, int& rephase_limit) {
    const int factor[4] = {8192, 4096, 2048, 1024};
    const int rephase_threshold = 2000000;
    const double threshold_factor = 0.9;

    // Decrease the threshold based on the number of conflicts
    threshold *= (rephases > 1000000) ? 0.95 : 0.9;

    // Calculate index into factor array based on number of conflicts
    int index = (rephases <= 300000) ? rephases/100000 : 3;

    // Increase rephase_limit by the corresponding factor
    rephase_limit = std::max(0, rephase_limit + factor[index]);

    // Additional optimization: rephase when the number of conflicts exceeds a certain threshold
    if (rephases >= rephase_threshold) {
        rephases = 0; // Reset rephases counter
    }
}
