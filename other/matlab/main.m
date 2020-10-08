clear all;

global prob_map lower upper;
prob_map_img = imread('prob_map_2.png');
prob_map = prob_map_img(:,:,1);

wps = 16;
lower = 0;
upper = length(prob_map_img);
x0 = rand(wps/2,2)*upper;
lb = ones(wps/2,2)*lower;
ub = ones(wps/2,2)*upper;


options = optimoptions('fmincon','FiniteDifferenceStepSize',0.05,'Display','notify');
[x,end_cost,exitflag,output] = fmincon(@cost_func,x0,[],[],[],[],lb,ub,[],options);


starting_cost = cost_func(x0);
fprintf('Done after %i iterations\n\n' , output.iterations)
fprintf('Cost of x0 = %.2f \n', starting_cost)
fprintf('Cost of x = %.2f \n', end_cost)
fprintf('Cost difference = %.2f \n',end_cost-starting_cost)

clf
hold on
axis tight
uistack(image([lower upper],[lower upper],prob_map_img)); 


plot(x0(:,1),x0(:,2),'linewidth',3,'color','g')
plot(x(:,1),x(:,2),'linewidth',3,'color','r')
