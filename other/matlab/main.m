clear all;

rng default
global prob_map radius;
prob_map_img = imread('prob_map.png');
prob_map = prob_map_img(:,:,1);

wps = 8;
radius = 2;

lower = 1;
upper = length(prob_map_img);




x0 = rand(wps,2)*upper;
lb = ones(wps,2)*lower;
ub = ones(wps,2)*upper;
options_rough = optimoptions('fmincon','FiniteDifferenceStepSize',0.1,'Display','notify', 'PlotFcn', {@optimplotfval});
options_fine = optimoptions('fmincon','Display','notify', 'PlotFcn', {@optimplotfval});

tic
[x,end_cost_1,~,~] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options_rough);
toc
% tic
% [x,end_cost_2,exitflag,output] = fmincon(@cost_func,x,[],[],[],[],lb,ub,[],options_fine);
% toc

% lb = ones(wps*2,1)*lower;
% ub = ones(wps*2,1)*upper; 
% options = optimoptions('ga','PlotFcn',{@gaplotbestf},'UseVectorized', false,'UseParallel', false);
% [x,end_cost,exitflag,output] = ga(@cost_func_ga,wps*2,[],[],[],[],lb,ub,[],options);
% x = reshape(x,[wps,2]);

% options = optimoptions('particleswarm','SwarmSize',50);
% [x,end_cost,exitflag,output] = particleswarm(@cost_func_ga,wps*2,lb,ub,options)

%%
starting_cost = cost_func(x0);
fprintf('Done after %i iterations\n\n' , output.iterations)
fprintf('Cost of x0 = %.2f \n', starting_cost)
fprintf('end_cost_1 = %.2f, end_cost_2 = %.2f \n', end_cost_1, end_cost_2)
fprintf('Cost difference = %.2f \n',end_cost_2-starting_cost)


%%
clf
figure(1)
hold on
axis tight equal
uistack(image([lower upper],[lower upper],prob_map_img)); 
plot(x0(:,1),x0(:,2),'linewidth',3,'color','g')
plot(x(:,1),x(:,2),'r-','linewidth',3)
plot(x(:,1),x(:,2),'bo','linewidth',3)
