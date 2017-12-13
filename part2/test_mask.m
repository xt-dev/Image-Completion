im = imread('./1.jpg');
mask = create_mask(im);
figure();
imshow(mask);