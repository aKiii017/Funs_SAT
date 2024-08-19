bool restart_condition(int lbd_queue_size, double fast_lbd_sum, double slow_lbd_sum, int conflicts)
{
    return lbd_queue_size == 50 && 0.8 * fast_lbd_sum / lbd_queue_size > slow_lbd_sum / conflicts;
}
