function [x] = pabo(optim_alg, wps)
print("Start of PABO")

rng default

global prob_map show_graphs

lower = 1;
upper = length(prob_map);
if optim_alg == "fmincon"
    x0 = rand(wps,2)*upper;
    lb = ones(wps,2)*lower;
    ub = ones(wps,2)*upper;
    if show_graphs
        options = optimoptions('fmincon','Display','notify', 'PlotFcn', {@optimplotfval,@optimplotfunccount})
    else
        options = optimoptions('fmincon','Display','notify');
    end
    print("Starting fmincon")
    [x,end_cost,~,~] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options);
    print(strcat("Finished fmincon with end_cost=",num2str(end_cost)))
elseif optim_alg == "ga"
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions(@ga,'PlotFcn',{@gaplotbestf},'UseVectorized', false,'UseParallel', false);
    print("Starting GA")
    [x,end_cost,exitflag,output] = ga(@cost_func_ga,wps*2,[],[],[],[],lb,ub,[],options);
    print(strcat("Finished GA with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
else
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions('particleswarm','SwarmSize',200,'PlotFcn',{@pswplotbestf});
    print("Starting particleswarm")
    [x,end_cost,exitflag,output] = particleswarm(@cost_func_ga,wps*2,lb,ub,options);
    print(strcat("Finished particleswarm with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
end
end
