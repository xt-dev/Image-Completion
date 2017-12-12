function im = poissonBlend(im_s, mask_s, im_background)

	[imh, imw, nb] = size(im_background);
	im2var = zeros(imh, imw); % as map
	count = 0;
	maxy = 1;
	miny = imh;
	maxx = 1;
	minx = imw;
	for y = 1:imh
		for x = 1:imw
			if mask_s(y,x)
				count = count + 1;
				im2var(y,x) = count;
				maxy = max(maxy, y); % find boundary
				miny = min(miny, y);
				maxx = max(maxx, x);
				minx = min(minx, x);
			end
		end
	end

	v1 = poissonBlendOneDim(im_s(:,:,1), mask_s, im_background(:,:,1), miny, maxy, minx, maxx, im2var);
	v2 = poissonBlendOneDim(im_s(:,:,2), mask_s, im_background(:,:,2), miny, maxy, minx, maxx, im2var);
	v3 = poissonBlendOneDim(im_s(:,:,3), mask_s, im_background(:,:,3), miny, maxy, minx, maxx, im2var);

	im = im_background;
	im_bf = im_background;
	for y = miny:maxy
		for x = minx:maxx
			if mask_s(y,x)
				im(y,x,1) = v1(im2var(y,x));
				im(y,x,2) = v2(im2var(y,x));
				im(y,x,3) = v3(im2var(y,x));
				im_bf(y,x,:) = im_s(y,x,:);
			end
		end
	end

end
