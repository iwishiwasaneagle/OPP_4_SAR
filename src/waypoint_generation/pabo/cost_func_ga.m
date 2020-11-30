function c = cost_func_ga(x_inp,home_wp,prob_map, radius, unit_endurance, unit_endurance_miss_const, prob_accum_const)
    len = length(x_inp);
    x = reshape(x_inp,[len/2,2]);    
    c = cost_func(x,home_wp,prob_map, radius, unit_endurance, unit_endurance_miss_const, prob_accum_const);
end