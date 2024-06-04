void rephase(int& rephases, int& threshold, int& rephase_limit) {
    const int factor[4] = {8192, 4096, 2048, 1024};
    
    //decrease the threshold based on the number of conflicts
    threshold *= (rephases > 1000000) ? 0.95 : 0.9;

    //if the number of conflicts is less than or equal to 300000, increase rephase_limit by the corresponding factor, else use the last factor
    if (rephases <= 300000)
    {
        rephase_limit += factor[rephases/100000];
    }
    else
    {
        rephase_limit += factor[3];
    }
    
    //ensure rephase_limit is not less than 0
    rephase_limit = std::max(0, rephase_limit);
}
