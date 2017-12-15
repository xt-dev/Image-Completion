function [mask, score] = find_mask(patch, sample, objmask, bdtop, bdbottom, bdleft, bdright)

	% return mask & score (sum of mincost for 4 masks)

	% use buildErrpatch and cut from MP2
	[patchh, patchw, k] = size(patch);
	score = 0;
	
	% mask 1: LEFT: MP2
	errpatch = buildErrpatch(permute(patch(:, 1:bdleft, :), [2 1 3]), permute(sample(:, 1:bdleft, :), [2 1 3]), permute(objmask(:, 1:bdleft, :), [2 1 3]));
	[curr, cost] = cut(errpatch);
	if cost < 200
		score = score + cost;
		mask1 = [curr; ones(patchw - bdleft, patchh)];
		mask1 = transpose(mask1);
	else
		mask1 = ones(patchh, patchw);
	end
% 	disp(cost);
% 	imshow(mask1);

	% mask 2: RIGHT
	errpatch = buildErrpatch(permute(patch(:, patchw-bdright+1:patchw, :), [2 1 3]), permute(sample(:, patchw-bdright+1:patchw, :), [2 1 3]), permute(objmask(:, patchw-bdright+1:patchw, :), [2 1 3]));
	[curr, cost] = cut(errpatch);
	if cost < 200
		score = score + cost;
		mask2 = [ones(patchw - bdright, patchh); ~curr];
		mask2 = transpose(mask2);
	else
		mask2 = ones(patchh, patchw);
	end
% 	imshow(mask2);
% 	disp(cost);

	% mask 3: TOP: MP2
	errpatch = buildErrpatch(patch(1:bdtop, :, :), sample(1:bdtop, :, :), objmask(1:bdtop, :, :));
	[curr, cost] = cut(errpatch);
	if cost < 300
		score = score + cost;
		mask3 = [curr; ones(patchh - size(curr, 1), patchw)];
	else
		mask3 = ones(patchh, patchw);
	end
		
% 	disp(cost);
% 	imshow(mask3);

	% mask 4: BOTTOM
	errpatch = buildErrpatch(patch(patchh-bdbottom+1:patchh, :, :), sample(patchh-bdbottom+1:patchh, :, :), objmask(patchh-bdbottom+1:patchh, :, :));
	[curr, cost] = cut(errpatch);
	if cost < 300
		score = score + cost;
		mask4 = [ones(patchh - size(curr, 1), patchw); ~curr];
	else
		mask4 = ones(patchh, patchw);
	end
% 	disp(cost);
% 	imshow(mask4);

	mask = mask1 & mask2 & mask3 & mask4; % find center region
	
	%% smooth
	% to prevent a bug in poisson blending _(:???)_
	for i=2:patchh-1
		for j=2:patchw-1
			if mask(i, j) == 1 && sum(sum(mask(i-1:i+1, j-1:j+1))) < 3
				mask(i, j) = 0;
			end
		end
	end

	mask = objmask(:, :, 1) | mask;
	imshow(mask);
	
	mask = cat(3, mask, mask, mask);

end
