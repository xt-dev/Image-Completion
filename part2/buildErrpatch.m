function errpatch = buildErrpatch(patch, im, objmask)

errpatch = patch(:,:,1);
patch = rgb2lab(patch);
im = rgb2lab(im);
[h, w] = size(errpatch);
diff = (patch - im).^2;
for i = 1:h
	for j = 1:w
		if objmask(i, j) == 1
			errpatch(i,j) = 1000;
		else
			errpatch(i,j) = sum(diff(i,j));
		end
	end
end
% disp(max(max(errpatch(i,j))));
