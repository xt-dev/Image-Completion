function output = exemplar_inpainting(orig, mask, patchsize)
	target_region = mask;
	source_region = ~mask;
	img = orig;
	[h,w] = size(img)
	index = reshape(1:h*w,h,w); % create index map for image

	% define isophote
	Ix = zeros(h,w,3);
	Iy = zeros(h,w,3);
	for i=1:3
		[Ix(:,:,i), Iy(:,:,i)] = gradient(img(:,:,i));
	end
	Ix = sum(Ix,3)/(3*255);
	Iy = sum(Iy,3)/(3*255);

	% rotate gradient
	temp = Ix;
	Ix = -Iy;
	Iy = temp

	% initialize confidence with hole as 1 and other as 0
	confidence = source_region

	% initialize data 
	data = -0.1*ones(h,w)

	while any(target_region(:))
		% Find contour & normalized gradients of fill region
		temp = find(conv2(double(target_region),[1,1,1;1,-8,1;1,1,1],'same') > 0);

		[Nx,Ny] = gradient(double(~target_region)); % Marcel 11/30/05
		%[Nx,Ny] = gradient(~target_region);         % Original
		N = [Nx(temp(:)) Ny(temp(:))];
		N = normr(N);  
		N(~isfinite(N))=0; % handle NaN and Inf

		% Compute confidences along the fill front
		for k=temp'
		Hp = getpatch(sz,k,psz);
		q = Hp(~(target_region(Hp)));
		C(k) = sum(C(q))/numel(Hp);
		end

		% Compute patch priorities = confidence term * data term
		D(temp) = abs(Ix(temp).*N(:,1)+Iy(temp).*N(:,2)) + 0.001;
		priorities = C(temp).* D(temp);

		% Find patch with maximum priority, Hp
		[~,ndx] = max(priorities(:));
		p = temp(ndx(1));
		[Hp,rows,cols] = getpatch(sz,p,psz);
		toFill = target_region(Hp);

		% Find exemplar that minimizes error, Hq
		Hq = bestexemplar(img,img(rows,cols,:),toFill',sourceRegion);

		% Update fill region
		toFill = logical(toFill);                 % Marcel 11/30/05
		target_region(Hp(toFill)) = false;

		% Propagate confidence & isophote values
		C(Hp(toFill))  = C(p);
		Ix(Hp(toFill)) = Ix(Hq(toFill));
		Iy(Hp(toFill)) = Iy(Hq(toFill));

		% Copy image data from Hq to Hp
		ind(Hp(toFill)) = ind(Hq(toFill));
		img(rows,cols,:) = ind2img(ind(rows,cols),origImg);  
	end
end