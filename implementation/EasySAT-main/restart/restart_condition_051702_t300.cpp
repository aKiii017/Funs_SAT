bool restart_condition(int lbd_queue_size, double fast_lbd_sum, double slow_lbd_sum, int conflicts)
{
    const int lbd_queue_size_threshold = 25;
    const int conflicts_threshold = 75;
    const double fast_lbd_avg_threshold = 2.0;
    const double slow_lbd_avg_threshold = 0.05;
    const double conflict_rate_threshold = 0.05;

    double fast_lbd_avg;
    double slow_lbd_avg;
    double conflict_rate;

    // Calculate average LBD sums
    if (lbd_queue_size > 0) 
    {
        fast_lbd_avg = static_cast<double>(fast_lbd_sum) / lbd_queue_size;
        slow_lbd_avg = static_cast<double>(slow_lbd_sum) / conflicts;
        conflict_rate = static_cast<double>(conflicts) / lbd_queue_size;

        // Check if all averages are within the thresholds
        return fast_lbd_avg > fast_lbd_avg_threshold * slow_lbd_avg &&
               conflict_rate > conflict_rate_threshold &&
               lbd_queue_size > lbd_queue_size_threshold &&
               conflicts > conflicts_threshold;
    }

    return false;
}
