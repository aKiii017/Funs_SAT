void rephase(int& rephases, int& threshold, int& rephase_limit) {
    static const int MAX_THRESHOLD = 1000000000;
    static const double CONFLICT_FACTOR = 0.95;
    static const double LOWER_BOUND_FACTOR = 0.9;
    static const int FACTOR_ARRAY[4] = {8192, 4096, 2048, 1024};
    static const int FACTOR_INDEX_3 = 3;

    const int REFRESH_RATE = 100000; 
    const int REPHASE_THRESHOLD = 2000000;
    const int REPHASE_FACTOR_INDEX = 1;
    const int FACTOR_FACTOR = 100;

    // Update the rephases
    rephases = std::max(0, rephases - REFRESH_RATE);

    // Update the threshold
    if (rephases <= REFRESH_RATE) {
        threshold *= CONFLICT_FACTOR;
    } else {
        threshold *= LOWER_BOUND_FACTOR;
    }
    threshold = std::min(threshold, MAX_THRESHOLD);

    // Calculate the index
    int index = rephases < FACTOR_FACTOR*REFRESH_RATE ? rephases/(FACTOR_FACTOR*REFRESH_RATE) : FACTOR_INDEX_3;

    // Update the rephase_limit
    rephase_limit = std::max(0, rephase_limit + FACTOR_ARRAY[index]);

    // Reset rephases if the condition is met
    if (rephases >= REPHASE_THRESHOLD) {
        rephases = 0;
    }
}
