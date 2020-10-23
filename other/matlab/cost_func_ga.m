function c = cost_func_ga(x_inp)
    len = length(x_inp);
    x = reshape(x_inp,[len/2,2]);    
    c = cost_func(x);
end