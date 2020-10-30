function [x] = pabo(inp_prob_map, optim_alg, wps)

rng default
global prob_map radius unit_endurance unit_endurance_miss_const prob_accum_const 

prob_map = double(inp_prob_map)/sum(inp_prob_map,'all');

radius = 2;

unit_endurance = 80;
unit_endurance_miss_const = 1;
prob_accum_const = 500;

lower = 1;
upper = length(prob_map);


if optim_alg == "fmincon"
    x0 = rand(wps,2)*upper;
    lb = ones(wps,2)*lower;
    ub = ones(wps,2)*upper;
    options = optimoptions('fmincon','Display','notify', 'PlotFcn', {@optimplotfval,@optimplotfunccount});

    [x,end_cost,~,~] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options);
elseif optim_alg == "ga"
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions(@ga,'PlotFcn',{@gaplotbestf},'UseVectorized', false,'UseParallel', false);
    [x,end_cost,exitflag,output] = ga(@cost_func_ga,wps*2,[],[],[],[],lb,ub,[],options);
    x = reshape(x,[wps,2]);
else
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions('particleswarm','SwarmSize',200,'PlotFcn',{@pswplotbestf});
    [x,end_cost,exitflag,output] = particleswarm(@cost_func_ga,wps*2,lb,ub,options);
    x = reshape(x,[wps,2]);
end
end
