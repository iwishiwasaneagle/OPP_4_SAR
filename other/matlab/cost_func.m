function c = cost_func(x_inp)
    global prob_map radius
    local_prob_map = prob_map;
    
    x1 = x_inp(1,:);
    c = 0;
    for i=2:length(x_inp)
        x2=x_inp(i,:);
        
        % Probability cost
        [lc, local_prob_map] = line_cost(x1,x2,local_prob_map, radius);
        c = c - lc;
                
        % Penalize distance
%         dist = vecnorm(x_inp-x2,2,2);
%         c = c + double(sum(80*heaviside(5-dist)));
        
        % Penalize crossings
%         [xi,yi] = polyxpoly([x1(1) x2(1)],[x1(2) x2(2)] ,x_inp(:,1),x_inp(:,2));        
%         c = c + 5*length(xi);          
%         x1 = x2;    
    end
end