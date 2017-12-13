function mask = create_mask(im)
	mask = zeros(600,800);
	for i=1:600
		for j=1:800
			if (im(i,j,1)+im(i,j,2)+im(i,j,3)) <= 3
				mask(i,j) = 1;
			else
				mask(i,j) = 0;
			end
		end
	end
end