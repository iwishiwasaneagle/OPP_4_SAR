function stop = plotoptimfunc_line(x,~,state)
    global prob_map radius
    persistent line_plot_obj %poly_plot_obj 
    
%     poly = polybuffer(x,'Lines',radius);
       
    if state == "init"        
        hold on
        %poly_plot_obj = patch('XData',poly.Vertices(:,1),'YData',poly.Vertices(:,2),'FaceColor','red','FaceAlpha',.3);
        line_plot_obj = plot(x(:,1), x(:,2),'Color','red','Linewidth',3);
        
        %axis equal
        h = surf(prob_map);
        z = get(h,'ZData');
        set(h,'ZData',z-1);
        xlabel('x (unit)');
        ylabel('y (unit)');
        title('XY graph w/ heatmap');
    else
        %set(poly_plot_obj,'XData',poly.Vertices(:,1),'YData',poly.Vertices(:,2));
        set(line_plot_obj,'XData',x(:,1), 'YData', x(:,2));
    end
    
    stop = false;
end

