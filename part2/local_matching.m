function local_matching(~)

	% starter code for local context matching
	
	close all
	
	im = im2double(imread('1.jpg'));
	local_matching_single(im);
	
	im = im2double(imread('3.jpg'));
	local_matching_single(im);

end
