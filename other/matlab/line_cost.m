function [cost, updated_prob_map] = line_cost(x1,x2,prob_map,r)
    c = 0;

    x = linspace(x1(1),x2(1),10);
    y = linspace(x1(2),x2(2),10);
    
    cost = 0;
    
    local_prob_map = prob_map;
    for i = 1:length(x)
        [c,local_prob_map,~] = position_cost([x(i),y(i)],r,local_prob_map);
        cost = cost + c;
    end
    
    updated_prob_map = local_prob_map;
    
end

