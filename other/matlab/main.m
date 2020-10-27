clear all;

rng default
global prob_map radius unit_endurance unit_endurance_miss_const prob_accum_const 
prob_map_img = imread('prob_map_2.png');
prob_map_img = imresize(prob_map_img,[20 20]);

prob_map = prob_map_img(:,:,1);
prob_map = double(prob_map)/sum(prob_map,'all');

wps = 8;
radius = 2;

unit_endurance = 80;
unit_endurance_miss_const = 1;
prob_accum_const = 500;

lower = 1;
upper = length(prob_map_img);

optim_alg = "particleswarm";

if optim_alg == "fmincon"
    x0 = rand(wps,2)*upper;
    lb = ones(wps,2)*lower;
    ub = ones(wps,2)*upper;
    options = optimoptions('fmincon','Display','notify', 'PlotFcn', {@plotoptimfunc_line,@optimplotfval,@optimplotfunccount});

    tic
    [x,end_cost,~,~] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options);
    toc
elseif optim_alg == "ga"
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions('ga','PlotFcn',{@gaplotbestf},'UseVectorized', false,'UseParallel', false);
    [x,end_cost,exitflag,output] = ga(@cost_func_ga,wps*2,[],[],[],[],lb,ub,[],options);
    x = reshape(x,[wps,2]);
else
    lb = ones(wps*2,1)*lower;
    ub = ones(wps*2,1)*upper; 
    options = optimoptions('particleswarm','SwarmSize',200,'PlotFcn',{@pswplotbestf});
    [x,end_cost,exitflag,output] = particleswarm(@cost_func_ga,wps*2,lb,ub,options);
    x = reshape(x,[wps,2]);
end
%%
if optim_alg == "fmincon"
    starting_cost = cost_func(x0);
    fprintf('Done after %i iterations\n\n' , output.iterations)
    fprintf('Cost of x0 = %.2f \n', starting_cost)
    fprintf('Cost difference = %.2f \n',end_cost-starting_cost)
end    
   
fprintf('end_cost = %.2f\n', end_cost)
fprintf('Distance = %.2f \n',sum(vecnorm(x(2:end,:)-x(1:end-1,:),2,2),'all'))


%%
clf
figure
hold on
axis tight equal
uistack(image([lower upper],[lower upper],prob_map_img)); 
if optim_alg == "fmincon"
    plot(x0(:,1),x0(:,2),'linewidth',3,'color','g')
end
plot(x(:,1),x(:,2),'r-','linewidth',3)
plot(x(:,1),x(:,2),'bo','linewidth',3)
