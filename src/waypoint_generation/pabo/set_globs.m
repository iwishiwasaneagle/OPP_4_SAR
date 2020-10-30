function out = set_globs(local_prob_map, local_radius, local_unit_endurancel, ocal_unit_endurance_miss_const, local_prob_accum_const)
    global prob_map radius unit_endurance unit_endurance_miss_const prob_accum_const 

    prob_map = local_prob_map;
    radius = local_radius;
    unit_endurance = local_unit_endurance;
    unit_endurance_miss_const = local_unit_endurance_miss_const;
    prob_accum_const = local_prob_accum_const;

    out = 1;
end