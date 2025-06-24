tol = 1e-12;
lambda = 1e-3;
filename = 'matlab_exe.txt';
V_obs=load('observation.txt')';
B=load('params.txt');
waitForPythonSignal()
for iter = 1:20
    % Evaluate the forward model at the current guess
    V_model = Site_1_forward();
    % Compute the residual (misfit)
    r = V_model - V_obs;
    
    % Display the current cost (optional)
	if iter>1
        prev_cost=cost;cost = norm(r)^2;
    endfprintf('Iteration %d: Cost = %e\n', iter, cost);
    
    % Compute the numerical Jacobian J (size: length(V_obs) x length(B))
    nB = numel(B);
    nV = numel(V_obs);
    J = zeros(nV, nB);
    delta = B.*0.1;
    for i = 1:nB
        B_perturbed = B;
        B_perturbed(i) = B_perturbed(i) + delta(i);
        writematrix(B_perturbed,'params.txt');
        fid = fopen('matlab_signal.txt', 'w');
        fprintf(fid, 'done');
        fclose(fid);
	    system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git pull origin master"')
	    system('git add params.txt')
	    system('git add matlab_signal.txt')
	    system('git commit -m "Auto update params and signal file"')
	    system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git push origin master"')	
        pause(300)
        waitForPythonSignal()
        % extract and allign
        V_perturbed = Site_1_forward();
        J(:, i) = (V_perturbed - V_model) / delta(i);
    end
    
    % Gauss-Newton step: Solve (J'*J) * dB = -J'*r
    dB = - (J' * J + lambda * eye(nB)) \ (J' * r);
    
    % Update parameters
    B = B + dB;
    writematrix(B,'params.txt');
    fid = fopen('matlab_signal.txt', 'w');
    fprintf(fid, 'done');
    fclose(fid);
    pause(300)
    waitForPythonSignal()
    % Check for convergence based on the update magnitude
    if norm(dB) < tol
        fprintf('Converged at iteration %d\n', iter);
        break;
    end
    if iter>1
        if prev_cost < cost*1.01
            fprintf('Converged at iteration %d\n', iter);
            break;
        end
    end
end
sd   = sqrt(diag(inv(J'*J)*mean(r.*r)));
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
	system('C:\Users\m10921371\AppData\Local\Programs\Git\git-bash.exe -c "git pull origin master"')
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

