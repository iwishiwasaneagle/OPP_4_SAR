function [c, prob_map] = line_cost(x1,x2,prob_map)
    upper = size(prob_map);
    lower = 1;
    c = 0;
    [x_arr,y_arr] = bresenham(x1(1),x1(2),x2(1),x2(2));
    for j=1:length(x_arr)
        x = x_arr(j);
        y = y_arr(j);
        truth = [[x y]<lower [x y]>upper];
        
        if any(truth)
            c = c + double(intmax('uint8'));
        else 
            c = c - double(prob_map(x,y));
            prob_map(x,y) = - intmax('uint16');
        end
    end
    
    c = double(c);
end

