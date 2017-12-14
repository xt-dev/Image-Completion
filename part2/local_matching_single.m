function local_matching_single(loc, withmask)

	addpath(loc)

	target = im2double(imread('input.jpg'));

	if withmask == false
		% get mask
		objmask = getMask(target);
		imwrite(objmask, 'mask.jpg');
		objmask = cat(3, objmask, objmask, objmask);
	else
		objmask = im2double(imread('mask.jpg'));
	end
	target = target .* ~objmask;

	[h, w, k] = size(target);
	[h1, w1, h2, w2] = find_rect(target);

	border = 100;
	top = max(1, h1 - border); % overflow
	bottom = min(h, h2 + border); 
	left = max(1, w1 - border); 
	right = min(w, w2 + border);
	bdtop = min(border, h1 - 1); % valid cut region
	bdbottom = min(border, h - h2);
	bdleft = min(border, w1 - 1);
	bdright = min(border, w - w2);

	%% to show rectangle (debug)
	% figure
	% imshow(target)
	% hold on
	% ii = [x1, x1, x2, x2, x1];
	% jj = [y1, y2, y2, y1, y1];
	% plot(jj, ii, 'r-', 'LineWidth', 1);
	% hold on
	% ii = [top, top, bottom, bottom, top];
	% jj = [left, right, right, left, left];
	% plot(jj, ii, 'b-', 'LineWidth', 1);

	%% build map
	
	c = containers.Map;
	fid = fopen('dist.txt');
	tline = fgetl(fid);
	while ischar(tline)
		par = strsplit(tline, ': ');
		c(par{1}) = str2double(par{2});
		tline = fgetl(fid);
	end
	fclose(fid);
	
	%% add for loop here
	score_list = zeros(20, 1);
	dinfo = dir(sprintf('%s/20*.jpg', loc));
	c1 = containers.Map;
	for i = 1:length(dinfo)
		
		thisfilename = dinfo(i).name;
		c1(int2str(i)) = thisfilename;
		
		im = im2double(imread(thisfilename)); % choose top 20 semantic matching images
		
		%% find mask
		patch = target(top:bottom, left:right, :);
		sample = im(top:bottom, left:right, :);
		[mask, cutcost] = find_mask(patch, sample, bdtop, bdbottom, bdleft, bdright);

		%% blending
		mask_s = zeros(h, w, 3); % same size as background
		mask_s(top:bottom, left:right, :) = mask;
		im_s = zeros(h, w, 3); % same size as background
		im_s(top:bottom, left:right, :) = sample;
		[poisson, blendcost] = poissonBlend(im_s, mask_s, target);
		% figure
		% imshow(poisson);
		imwrite(poisson, sprintf('%s/after%d.jpg', loc, i));
		% NO [index] with cost [cost];
		score_list(i) = cutcost * 10^(-6) + blendcost * 10^(-1) + 2*c(thisfilename); % sum of 4 cut cost	
		fprintf('No. %d %s with cost %f\n', i, thisfilename, score_list(i));  	
	end
	
	% find min5
	sorted = sort(score_list);
	for i = 1:5 % best 5
		idx = find(score_list == sorted(i));
		% BEST [rank]: [index] with cost [cost]
		fprintf('BEST %d: no. %d %s with cost %f\n', i, idx, c1(int2str(idx)), score_list(idx));
	end

end
