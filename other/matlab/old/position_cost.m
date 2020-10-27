function [cost,updated_prob_map,area_covered] = position_cost(pos,r,prob_map)
    num_verts  = 360;
    L = linspace(0,2*pi - (2*pi)/num_verts,num_verts);
    
    circ_x = pos(1)+r.*cos(L);
    circ_y = pos(2)+r.*sin(L);
    
    circle = polyshape(circ_x, circ_y);        
    
    [max_x,max_y] = size(prob_map);
    
    [x_tmp, y_tmp] = meshgrid(1:max_x, 1:max_y);
    x = reshape(x_tmp,max_x^2,1);
    y = reshape(y_tmp,max_y^2,1);
    area_covered = zeros(length(x),1);
    cost = 0;
    
    local_prob_map = prob_map;
    
    for i = 1:length(x)
        c1 = [x(i),y(i)];
        c2 = [x(i)+1,y(i)];
        c3 = [x(i),y(i)+1];
        c4 = [x(i)+1,y(i)+1];
        
        if x(i) > max_x || y(i) > max_y
            break
        end

        dc1 = norm(pos - c1);
        dc2 = norm(pos - c2);
        dc3 = norm(pos - c3);
        dc4 = norm(pos - c4);

        dists = [dc1 dc2 dc3 dc4] < r;
        
        if all(dists)
            area_covered(i) = 1;            
            cost = cost + local_prob_map(y(i),x(i));
            local_prob_map(y(i),x(i)) = 0;
        elseif any(dists)
            poly = [c1; c2; c4; c3; c1];
            poly = polyshape(poly(:,1), poly(:,2));
            polyout = intersect(poly,circle);
            area = polyout.area;
            area_covered(i) = area;
            cost = cost + local_prob_map(y(i),x(i))*area;
            local_prob_map(y(i),x(i)) = local_prob_map(y(i),x(i))*(1-area);
        end
    end
    
    area_covered = reshape(area_covered,max_x,max_y);
    updated_prob_map = local_prob_map;
    cost = sum(cast(prob_map,'double').*area_covered,'all');
end

