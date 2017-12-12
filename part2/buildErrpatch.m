function errpatch = buildErrpatch(patch, im)

errpatch = patch(:,:,1);
[h, w] = size(errpatch);
diff = (patch - im).^2;
for i = 1:h
	for j = 1:w
		errpatch(i,j) = sum(diff(i,j));
	end
end
