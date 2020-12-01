function [x] = pabo(optim_alg,wps,home_wp,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const,show_graphs)
disp("Start of PABO")

rng default

x_lims = find(diff(mean(prob_map,1))~=0);
y_lims = find(diff(mean(prob_map,2))~=0);
    
lb = zeros(wps,2);
lb(:,1) = x_lims(1)-1;
lb(:,2) = y_lims(1)-1;

ub = zeros(wps,2);       
ub(:,1) = x_lims(end)+1;
ub(:,2) = y_lims(end)+1;

use_parallel = true;

tic
if optim_alg == "fmincon"
    x0 = zeros(wps,2);
    x0(:,1) = x_lims(1)+rand(wps,1)*(x_lims(end)-x_lims(1));
    x0(:,2) = y_lims(1)+rand(wps,1)*(y_lims(end)-y_lims(1));
    
    options = optimoptions('fmincon','Display','notify', 'UseParallel',use_parallel);
    if show_graphs
        options = optimoptions(options, 'PlotFcn', {@optimplotfval,@optimplotfunccount});
    end
    disp("Starting fmincon")
    [x,end_cost,~,~] = fmincon(@(x) cost_func(x,home_wp,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),x0,[],[],[],[],lb,ub,[],options);
    disp(strcat("Finished fmincon with end_cost=",num2str(end_cost)))
    
elseif optim_alg == "ga"
    lb = reshape(lb',wps*2,1);
    ub = reshape(ub',wps*2,1);
    
    options = optimoptions(@ga,'UseVectorized', false,'UseParallel', use_parallel);
    if show_graphs
        options = optimoptions(options,'PlotFcn',{@gaplotbestf});
    end
    disp("Starting GA")
    [x,end_cost,exitflag,output] = ga(@(x) cost_func_ga(x,home_wp,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),wps*2,[],[],[],[],lb,ub,[],options);
    disp(strcat("Finished GA with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
else
    lb = reshape(lb',wps*2,1);
    ub = reshape(ub',wps*2,1);
    
    options = optimoptions('particleswarm','SwarmSize',50,'UseVectorized', false,'UseParallel', use_parallel);
    if show_graphs 
        options = optimoptions(options,'PlotFcn',{@pswplotbestf});
    end
    disp("Starting particleswarm")
    [x,end_cost,exitflag,output] = particleswarm(@(x) cost_func_ga(x,home_wp,prob_map,radius,unit_endurance,unit_endurance_miss_const,prob_accum_const),wps*2,lb,ub,options);
    disp(strcat("Finished particleswarm with end_cost=",num2str(end_cost)))
    x = reshape(x,[wps,2]);
end
toc
end
