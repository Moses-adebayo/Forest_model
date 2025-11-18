% Wait until all files exist
while true
    existAll = true;
    for i = 1:10
        if ~isfile(fullfile(sprintf('Site1_param%d', i), 'data_set_edit.txt'))
            existAll = false;
            break;
        end
    end
    
    if existAll
        disp('All ATS results found... proceed');
        break;
    else
        pause(600); % wait 600 seconds (10 minutes)
    end
end

% Loop forward and delete files
for i = 0:9
    forward(num2str(i));  % Call the forward function
end    
for j = 1:10
    filePath = fullfile(sprintf('Site1_param%d', j), 'data_set_edit.txt');
    delete(filePath);  % Delete the file 
end