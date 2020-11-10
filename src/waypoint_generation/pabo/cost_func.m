function cost = cost_func(x_inp,prob_map, radius, unit_endurance, unit_endurance_miss_const, prob_accum_const)
    cost = 0;
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % ACCUMULATED PROBABILITY %
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    [max_x,max_y] = size(prob_map);

    r = radius;
    r_extra_search = 1;

    
    poly = polybuffer(x_inp,'Lines',r);
    poly_fat = polybuffer(x_inp,'Lines', r+r_extra_search);

    [x, y] = meshgrid(1:max_x, 1:max_y);
    x = reshape(x,max_x^2,1);
    y = reshape(y,max_y^2,1);

    [in_fat,~] = inpolygon(x,y,poly_fat.Vertices(:,1),poly_fat.Vertices(:,2));
    [in,~] = inpolygon(x,y,poly.Vertices(:,1),poly.Vertices(:,2));
    
    local_prob_map = zeros(max_x,max_y);
    
    in = reshape(in,max_x,max_y);
    found = find(in_fat);
    
    for ind=1:length(found)
        i=found(ind);
        xi = x(i);
        yi = y(i);

        if xi+1>max_x || yi+1>max_y  % already naturally capped for -ve values by `inpolygon`
            continue
        end

        c2 = [xi+1,yi];
        c3 = [xi,yi+1];
        c4 = [xi+1,yi+1];

        truth_arr = [in(c2(2),c2(1)), in(c3(2),c3(1)), in(c4(2),c4(1))] > 0; % c1 is always in `in`

        if all(truth_arr)
            local_prob_map(i) = prob_map(i);
        else
            c1 = [xi, yi];
            grid_square = [c1; c2; c4; c3; c1];
            grid_square = polyshape(grid_square);
            polyout = intersect(grid_square,poly);
            local_prob_map(i) = prob_map(i)*polyout.area;
        end
    end 
    
    cost = cost - prob_accum_const*sum(local_prob_map,'all');
    
    %%%%%%%%%%%%%
    % ENDURANCE %
    %%%%%%%%%%%%%
    
    dists = vecnorm(x_inp(2:end,:)-x_inp(1:end-1,:),2,2);
    dist = sum(dists,'all');
    cost = cost + unit_endurance_miss_const*abs(dist/unit_endurance);
end