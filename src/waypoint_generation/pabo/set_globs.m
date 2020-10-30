function out = set_globs(local_prob_map, local_radius, local_unit_endurance, local_unit_endurance_miss_const, local_prob_accum_const, only_accum_prob)
    global prob_map radius unit_endurance unit_endurance_miss_const prob_accum_const 

    prob_map = local_prob_map;
    radius = local_radius;
    unit_endurance = local_unit_endurance;
    unit_endurance_miss_const = local_unit_endurance_miss_const;
    prob_accum_const = local_prob_accum_const;

    if only_accum_prob == true
        unit_endurance_miss_const = 0;
        prob_accum_const = 1;
    end

    out = 1;
end