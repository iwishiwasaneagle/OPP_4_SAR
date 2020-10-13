clear all;

global prob_map ;
prob_map_img = imread('prob_map.png');
prob_map = prob_map_img(:,:,1);

wps = 25;

lower = 1;
upper = length(prob_map_img);


%%

% x0 = rand(wps,2)*upper;
% lb = ones(wps,2)*lower;
% ub = ones(wps,2)*upper;
% options = optimoptions('fmincon','FiniteDifferenceStepSize',0.05,'Display','notify');
% [x,end_cost,exitflag,output] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options);


lb = ones(wps*2,1)*lower;
ub = ones(wps*2,1)*upper;

hybridopts = optimoptions('fmincon','Display','iter','FiniteDifferenceStepSize',0.5);

options = optimoptions('ga','PlotFcn',{@gaplotbestf},'UseVectorized', false,'UseParallel', true,'HybridFcn',{@fmincon,hybridopts});
[x,end_cost,exitflag,output] = ga(@cost_func_ga,wps*2,[],[],[],[],lb,ub,[],options);
x = reshape(x,[wps,2]);

%%
% starting_cost = cost_func_ga(x0);
% fprintf('Done after %i iterations\n\n' , output.iterations)
% fprintf('Cost of x0 = %.2f \n', starting_cost)
fprintf('Cost of x = %.2f \n', end_cost)
% fprintf('Cost difference = %.2f \n',end_cost-starting_cost)


%%
clf
figure(1)
hold on
axis tight equal
uistack(image([lower upper],[lower upper],prob_map_img)); 
% plot(x0(:,1),x0(:,2),'linewidth',3,'color','g')
plot(x(:,1),x(:,2),'r-','linewidth',3)
plot(x(:,1),x(:,2),'bo','linewidth',3)
