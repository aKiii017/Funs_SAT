bool restart_condition(int lbd_queue_size, double fast_lbd_sum, double slow_lbd_sum, int conflicts)
{
    if (lbd_queue_size < 15 || conflicts < 40)
        return false;

    double fast_lbd_avg = fast_lbd_sum / (lbd_queue_size + 1);
    double slow_lbd_avg = slow_lbd_sum / (conflicts + 1);
    double conflict_rate = static_cast<double>(conflicts) / (lbd_queue_size + 1);

    double threshold_fast = 1.5 * slow_lbd_avg;
    double threshold_slow = 0.025 * slow_lbd_avg;
    double threshold_conflict = 0.025;

    // Check each condition individually and perform an OR operation.
    bool condition_fast_avg = fast_lbd_avg > threshold_fast;
    bool condition_conflict_rate = conflict_rate > threshold_conflict;
    bool condition_slow_avg = fast_lbd_avg > threshold_slow;

    return condition_fast_avg || (condition_conflict_rate && !condition_slow_avg);
}
