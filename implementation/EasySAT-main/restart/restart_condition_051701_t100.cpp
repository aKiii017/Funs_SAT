bool restart_condition(int lbd_queue_size, double fast_lbd_sum, double slow_lbd_sum, int conflicts)
{
    if (lbd_queue_size < 20 || conflicts < 50) {
        return false;
    }

    double fast_lbd_avg = fast_lbd_sum / lbd_queue_size;
    double slow_lbd_avg = slow_lbd_sum / conflicts;
    double conflict_rate = static_cast<double>(conflicts) / lbd_queue_size;

    return fast_lbd_avg > (2 * slow_lbd_avg) && conflict_rate > 0.05;
}
