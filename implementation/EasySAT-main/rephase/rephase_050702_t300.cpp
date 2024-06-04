void rephase(int& rephases, int& threshold, int& rephase_limit) {
    constexpr double THRESHOLD_DECREMENT = 0.05;
    constexpr unsigned int REPHASE_LIMIT_INCREMENT = 8192;
    constexpr double BASE_THRESHOLD = 0.9;
    constexpr unsigned int REPHASE_LIMIT_MAX = 1 << 20; // Max rephase limit
    constexpr unsigned int REPHASE_LIMIT_INCREMENT_FACTOR = 1 << 13; // Increase factor for rephase limit

    // Update rephases
    ++rephases;

    // Apply rephase logic based on rephases count with improved conditions
    if (rephases > 5000) {
        threshold *= 0.85; // Decrease threshold slightly more aggressively
        rephase_limit += REPHASE_LIMIT_INCREMENT * 2; // Increase rephase limit more aggressively
    } else if (rephases > 3000) {
        threshold *= 0.9;
        rephase_limit += REPHASE_LIMIT_INCREMENT;
    } else if (rephases > 2000) {
        threshold *= 0.95;
        rephase_limit += REPHASE_LIMIT_INCREMENT/2;
    } else if (rephases > 1000) {
        threshold *= 0.97;
        rephase_limit += REPHASE_LIMIT_INCREMENT/4;
    }

    // Ensure threshold is not too low
    if (threshold < THRESHOLD_DECREMENT * BASE_THRESHOLD) {
        rephases = 0;
        threshold = BASE_THRESHOLD;
    }

    // Update rephase limit every REPHASE_LIMIT_INCREMENT_FACTOR rephases
    if (rephases % REPHASE_LIMIT_INCREMENT_FACTOR == 0) {
        rephase_limit += REPHASE_LIMIT_INCREMENT;
    }

    // Cap the rephase_limit
    if (rephase_limit > REPHASE_LIMIT_MAX) {
        rephase_limit = REPHASE_LIMIT_MAX;
    }
}
