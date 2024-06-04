void rephase(int& rephases, int& threshold, int& rephase_limit) {
    // Increment the number of conflicts since the last rephases
    rephases++;

    // Adjust the rephase limit depending on the number of conflicts
    if (rephases > 5000)
    {
        rephase_limit += 8192;
    }
    else if (rephases > 1000)
    {
        rephase_limit += 4096;
    }
    else if (rephases > 200)
    {
        rephase_limit += 2048;
    }

    // Decrease the threshold for rephasing to encourage more rephasing
    threshold *= (rephases > 5000) ? 0.8 : (rephases > 1000) ? 0.9 : (rephases > 200) ? 0.95 : 1.0;

    // Reset the number of conflicts if the threshold is low
    if (threshold < 0.05)
    {
        rephases = 0;
        threshold = 0.9;
    }
}
