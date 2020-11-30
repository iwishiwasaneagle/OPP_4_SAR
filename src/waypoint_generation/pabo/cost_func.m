function cost = cost_func(x_inp,home_wp,prob_map, radius, unit_endurance, unit_endurance_miss_const, prob_accum_const)
    cost = 0;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % ACCUMULATED PROBABILITY %
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    [max_x,max_y] = size(prob_map);

    r = radius;
    r_extra_search = 1;

    if ~all(home_wp<0)
        x_inp = [home_wp; x_inp; home_wp];
    end
    
    poly = polybuffer(x_inp,'Lines',r);
    poly_fat = polybuffer(x_inp,'Lines', r+r_extra_search);

    [x, y] = meshgrid(1:max_x, 1:max_y);
    x = reshape(x,[],1);
    y = reshape(y,[],1);

    [in_fat,~] = inpolygon(x,y,poly_fat.Vertices(:,1),poly_fat.Vertices(:,2));
    [in,~] = inpolygon(x,y,poly.Vertices(:,1),poly.Vertices(:,2));
    
    local_prob_map = zeros(max_x,max_y);
    
    in = reshape(in,max_x,max_y);
    found = find(in_fat);
    len_found = length(found);
    
    for ind=1:len_found
        found_i=found(ind);
        xi = x(found_i);
        yi = y(found_i);

        if xi+1>max_x || yi+1>max_y  % already naturally capped for -ve valu es by `inpolygon`
            continue
        end

        c2 = [xi+1,yi];
        c3 = [xi,yi+1];
        c4 = [xi+1,yi+1];

        truth_arr = [in(c2(2),c2(1)), in(c3(2),c3(1)), in(c4(2),c4(1))] > 0; % c1 is always in `in`
        
        local_prob_map_value = 0;
        if all(truth_arr)            
            prob = prob_map(yi,xi);            
            if (prob==0 && unit_endurance_miss_const>0)
                prob = -100;
            end            
            local_prob_map_value = prob;
        else
            c1 = [xi, yi];
            grid_square = [c1; c2; c4; c3; c1];
            grid_square = polyshape(grid_square);
            polyout = intersect(grid_square,poly);
            prob = prob_map(yi,xi);            
            if (prob==0 && unit_endurance_miss_const>0)
                prob = -10;
            end     
            local_prob_map_value = prob*polyout.area;
        end
        tmp = struct();
        tmp.xi = xi;
        tmp.yi = yi;
        tmp.val = local_prob_map_value;

        local_prob_map(yi,xi) = local_prob_map_value;
    end 
    cost = cost - prob_accum_const*sum(local_prob_map,'all');

    %%%%%%%%%%%%%
    % ENDURANCE %
    %%%%%%%%%%%%%
    
    dists = vecnorm(x_inp(2:end,:)-x_inp(1:end-1,:),2,2);
    d = sum(dists,'all');
    cost = cost + unit_endurance_miss_const*abs(d-unit_endurance);
end
