function [x] = pabo(optim_alg, wps)

rng default

global prob_map

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
