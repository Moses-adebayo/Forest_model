waitForPythonSignal()
V_obs=load('observation.txt')';
nV = numel(V_obs);
sim_obs=zeros(10,nV);
% Evaluate the forward model at the current guess
for i=1:10
    system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git pull origin ESMDA"')
    sim_obs(i,:)=Site_1_forward(i);
end
fid = fopen('matlab_forward.txt', 'w');
fprintf(fid, 'done');
fclose(fid);
system('git add params.txt')
system('git add matlab_forward.txt')
system('git commit -m "final iteration"')
system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git push origin ESMDA"')
writematrix(sim_obs,'forward_obs.txt');

function waitForPythonSignal(filename)
% waitForPythonSignal Pauses execution until the file contains 'done'
%
% Usage:
%   waitForPythonSignal()         % Uses default filename 'matlab_exe.txt'
%   waitForPythonSignal(fname)    % Uses the specified filename
%
% The function repeatedly checks the contents of the specified file.
% It pauses execution until the file's contents become 'done'.

    % Default filename if not provided
    if nargin < 1
        filename = 'matlab_exe.txt';
    end

    % Loop until the file exists and its content is 'done'
    while true
	system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git pull origin ESMDA"')
        if exist(filename, 'file')
            fid = fopen(filename, 'r');
            if fid ~= -1
                content = fscanf(fid, '%s');
                fclose(fid);
                if strcmp(content, 'done')
                    break;  % Exit the loop if content is 'done'
                end
            end
        end
        pause(180);  % Wait for 1 second before checking again
    end

    disp('MATLAB: Detected "done". Resuming MATLAB execution.');
end

