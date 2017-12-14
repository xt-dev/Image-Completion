function [inpaintedImg,C,D,fillMovie] = inpainting(origImg,mask,psz)

%% error check
% if ~ismatrix(mask); error('Invalid mask'); end
% if sum(sum(mask~=0 & mask~=1))>0; error('Invalid mask'); end
% if mod(psz,2)==0; error('Patch size psz must be odd.'); end

fillRegion = mask;

origImg = double(origImg);
img = origImg;
ind = img2ind(img);
sz = [size(img,1) size(img,2)];
sourceRegion = ~fillRegion;

% Initialize isophote values
[Ix(:,:,3), Iy(:,:,3)] = gradient(img(:,:,3));
[Ix(:,:,2), Iy(:,:,2)] = gradient(img(:,:,2));
[Ix(:,:,1), Iy(:,:,1)] = gradient(img(:,:,1));
Ix = sum(Ix,3)/(3*255); Iy = sum(Iy,3)/(3*255);
temp = Ix; Ix = -Iy; Iy = temp;  % Rotate gradient 90 degrees

% Initialize confidence and data terms
C = double(sourceRegion);
D = repmat(-.1,sz);
iter = 1;
% Visualization stuff
if nargout==4
  fillMovie(1).cdata=uint8(img); 
  fillMovie(1).colormap=[];
  origImg(1,1,:) = [0, 255, 0];
  iter = 2;
end

% Seed 'rand' for reproducible results (good for testing)
rand('state',0);

% Loop until entire fill region has been covered
while any(fillRegion(:))
  % Find contour & normalized gradients of fill region
  fillRegionD = double(fillRegion); % Marcel 11/30/05
  dR = find(conv2(fillRegionD,[1,1,1;1,-8,1;1,1,1],'same')>0);
  
  [Nx,Ny] = gradient(double(~fillRegion)); % Marcel 11/30/05
 %[Nx,Ny] = gradient(~fillRegion);         % Original
  N = [Nx(dR(:)) Ny(dR(:))];
  N = normr(N);  
  N(~isfinite(N))=0; % handle NaN and Inf
  
  % Compute confidences along the fill front
  for k=dR'
    Hp = getpatch(sz,k,psz);
    q = Hp(~(fillRegion(Hp))); % fillRegion?????????????????
    C(k) = sum(C(q))/numel(Hp);
  end
  
  % Compute patch priorities = confidence term * data term
  D(dR) = abs(Ix(dR).*N(:,1)+Iy(dR).*N(:,2)) + 0.001;
  priorities = C(dR).* D(dR);
  
  % Find patch with maximum priority, Hp
  [~,ndx] = max(priorities(:));
  p = dR(ndx(1));
  [Hp,rows,cols] = getpatch(sz,p,psz);
  toFill = fillRegion(Hp);
  
  % Find exemplar that minimizes error, Hq
  Hq = bestexemplar(img,img(rows,cols,:),toFill',sourceRegion);
  
  % Update fill region
  toFill = logical(toFill);                 % Marcel 11/30/05
  fillRegion(Hp(toFill)) = false;
  
  % Propagate confidence & isophote values
  C(Hp(toFill))  = C(p);
  Ix(Hp(toFill)) = Ix(Hq(toFill));
  Iy(Hp(toFill)) = Iy(Hq(toFill));
  
  % Copy image data from Hq to Hp
  ind(Hp(toFill)) = ind(Hq(toFill));
  img(rows,cols,:) = ind2img(ind(rows,cols),origImg);  

  % Visualization stuff
  if nargout==4
    ind2 = ind;
    ind2(logical(fillRegion)) = 1;
    fillMovie(iter).cdata=uint8(ind2img(ind2,origImg)); 
    fillMovie(iter).colormap=[];
  end
  iter = iter+1;
end

inpaintedImg = img;