function [h1, w1, h2, w2] = find_rect(im)

	% find the smallest rectangle containing the region
	% return upper-left corner & bottom-right corner

	[h, w, k] = size(im);

	h1 = 0; % initialize
	h2 = 0;
	w1 = 0;
	w2 = 0;

	for i = 2:h-1
		if h1 ~= 0
			break
		end
		for j = 2:w-1
			if sum(sum(im(i-1:i+1, j-1:j+1, :))) == 0
				h1 = i; % update top-most
				break
			end
		end
	end

	for i = h-1:-1:2
		if h2 ~= 0
			break
		end
		for j = 2:w-1
			if sum(sum(im(i-1:i+1, j-1:j+1, :))) == 0
				h2 = i; % update bottom-most
				break
			end
		end
	end

	for j = 2:w-1
		if w1 ~= 0
			break
		end
		for i = h1:h2 % narrowdown the scope
			if sum(sum(im(i-1:i+1, j-1:j+1, :))) == 0
				w1 = j; % update left-most
				break
			end
		end
	end

	for j = w-1:-1:2
		if w2 ~= 0
			break
		end
		for i = h1:h2
			if sum(sum(im(i-1:i+1, j-1:j+1, :))) == 0
				w2 = j; % update right-most
				break
			end
		end
	end

end
