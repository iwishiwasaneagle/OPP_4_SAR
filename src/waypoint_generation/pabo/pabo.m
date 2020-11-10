function [x] = pabo(optim_alg,wps,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const,show_graphs)
print("Start of PABO")

rng default

lower = 0;
upper = length(prob_map);

use_parallel = true;

tic
if optim_alg == "fmincon"
    x0 = rand(wps,2)*upper;
    lb = ones(wps,2)*lower;
    ub = ones(wps,2)*upper;    
    options = optimoptions('fmincon','Display','notify', 'PlotFcn', {@optimplotfval,@optimplotfunccount},'UseParallel',use_parallel);
    if show_graphs
        options = optimoptions(options, 'PlotFcn', {@optimplotfval,@optimplotfunccount});
    end
    print("Starting fmincon")
    [x,end_cost,~,~] = fmincon(@(x) cost_func(x,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),x0,[],[],[],[],lb,ub,[],options);
    print(strcat("Finished fmincon with end_cost=",num2str(end_cost)))
    
elseif optim_alg == "ga"
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions(@ga,'UseVectorized', false,'UseParallel', use_parallel);
    if show_graphs
        options = optimoptions(options,'PlotFcn',{@gaplotbestf});
    end
    print("Starting GA")
    [x,end_cost,exitflag,output] = ga(@(x) cost_func_ga(x,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),wps*2,[],[],[],[],lb,ub,[],options);
    print(strcat("Finished GA with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
else
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper;
    
    options = optimoptions('particleswarm','SwarmSize',50,'UseVectorized', false,'UseParallel', use_parallel);
    if show_graphs 
        options = optimoptions(options,'PlotFcn',{@pswplotbestf});
    end
    print("Starting particleswarm")
    [x,end_cost,exitflag,output] = particleswarm(@(x) cost_func_ga(x,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),wps*2,lb,ub,options);
    print(strcat("Finished particleswarm with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
end
toc
end
