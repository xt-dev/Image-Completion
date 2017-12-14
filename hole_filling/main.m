origImg = imread('./test_img.bmp');
mask = im2double(rgb2gray(imread('./test_mask.bmp')));
psz = 5;
im = inpainting(origImg,mask,psz);