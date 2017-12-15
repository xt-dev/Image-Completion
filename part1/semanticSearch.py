import gist
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2
import os
import sys
import pickle
from skimage import io, color
from skimage.transform import resize
#np.set_printoptions(threshold='nan')

def merge_two_dicts(x,y):
    z = x.copy()
    z.update(y)
    return z


if __name__ == "__main__":
    # if len(sys.argv) != 6:
    #     #print("usage: python semanticSearch.py input_image_path mask_path db_gist_file img_name_pickle_file outfile")
    #     print("usage: python semanticSearch.py input_image_path db_image_path mask_path db_gists_folder outfile")
    #     sys.exit(0)
    input_image_path = "in.jpg"#sys.argv[1] 
    db_image_path = "images_lake_small"#sys.argv[2]
    mask_path = "mask.jpg" #sys.argv[3] 
    db_gists_folder = "gists_lake_mt" #sys.argv[4]
    outfile= "out3"#sys.argv[5]
    gists_list = [] 
    imgs_list = []
    for filename in os.listdir(db_gists_folder):
        if filename.endswith(".npy"):
            #print(filename) 
            file_gist = np.load(db_gists_folder+"/" +filename)
            gists_list.append(file_gist)
        elif filename.endswith(".pickle"):
            with open(db_gists_folder+"/"+filename,"rb") as fp:
                file_dict = pickle.load(fp)
                imgs_list.append(file_dict)
    
    gists = []
    imgs = {}
    count = 0
    for i in range(len(gists_list)):
        for j in range(len(gists_list[0])):
            #print("i: {}".format(i))
            #print("j: {}".format(j))
            #print(imgs_list[0])
            try:
                imgs[count] = imgs_list[i][999-j]
                gists.append(gists_list[i][j])
            except Exception, e:
                continue
            count += 1
    gists = np.array(gists) 
    ##gist parameters
    number_blocks = 4
    orientations_per_scale = [8,8,4]
    #img_size = (600, 800)
    img_size = (192,256)

    ##query image
    #filename_input = "street_par28.jpg"
    filename_input = input_image_path
    img_input_rgb =  cv2.imread(filename_input)
    [h,w,_] =img_input_rgb.shape
    ##gist for the query image
    gist_input = gist.extract(img_input_rgb)

    ##gists of the images in the database
    #gists = np.load("./gists.npy")
    # gists = np.load(db_gist_file)

    ##mask = mask1 + mask2
    mask_rgb = io.imread(mask_path)
    #print(mask_rgb.shape) 
    mask_gray = cv2.cvtColor(mask_rgb, cv2.COLOR_BGR2GRAY)
    
   # mask1 = np.zeros((h,w))
   # cv2.circle(mask1,(w/4,h/3),50,255,thickness=-1)

   # mask2 = np.zeros((h,w))
   # cv2.circle(mask2,(w/2,int(h/1.5)),60,255,thickness=-1)
   # mask = mask1 + mask2

    mask_gray[mask_gray > 250] = 1
    mask = 1 - mask_gray.astype('uint8')
    #masked_img = cv2.bitwise_and(img_input_rgb, img_input_rgb, mask=mask)

    ##Calculate the weights for the gist
    s_h = np.linspace(0, img_size[0], num=number_blocks+1).astype("uint32")
    s_w = np.linspace(0, img_size[1], num=number_blocks+1).astype("uint32")
    block_weight = np.zeros((number_blocks, number_blocks))
    for y in range(number_blocks):
        for x in range(number_blocks):
            block = mask[s_h[y] +1:s_h[y+1], s_w[x]+1:s_w[x+1]]
            block_weight[y,x] = np.mean(block.flatten())
    #block_weight = np.tile(block_weight.flatten(), [1, np.sum(orientations_per_scale)])
    block_weight = np.tile(block_weight.flatten(), [1, np.sum(orientations_per_scale)*3])

    ##Calculate the distance between the query image and images in the database
    dist = gists - np.tile(gist_input, [gists.shape[0], 1])
    #print(block_weight)
    #print(gists.shape[0])
    dist = np.multiply(np.tile(block_weight, [gists.shape[0],1]), dist)
    dist = np.sum(dist**2, axis=1)

    ##Get the nearest images
    nearest_gist_num = 100
    nearest_list = dist.argsort()[:nearest_gist_num]

    # #with open("imgs.pickle","rb") as fb:
    # with open(img_name_pickle_file,"rb") as fb:
    #     imgs = pickle.load(fb)
    #with open("nearest.txt", "w") as f:
    # with open(outfile, "w") as f:
    #     for index in nearest_list:
    #         f.write(imgs[index] +"\n")
    
    img_input_lab = cv2.cvtColor(img_input_rgb, cv2.COLOR_BGR2LAB)
    
    color_dist_dict = {}
    total_dists = []
    for index in nearest_list:
        #print("Working on {}".format(imgs[index]))
        cur_img_path = imgs[index]
        img_db_rgb = cv2.imread(db_image_path +"/"+cur_img_path)
        if img_db_rgb.shape[0] != 192 or img_db_rgb.shape[1] != 256:
            total_dists.append((imgs[index], 10000))
            continue
        avg_dist = np.sum((img_db_rgb[:,:,0:3]-img_input_rgb[:,:,0:3])**2)/(img_size[0]*img_size[1])
        color_dist_dict[index] =  avg_dist
        #print("{}: {}".format(imgs[index],avg_dist))
        #total_dist = weight_c*avg_dist + weight_g*dist[index]
        #total_dists.append((imgs[index], total_dist))
    min_color_dist = 10000
    max_color_dist = 0
    for key in color_dist_dict:
        if(color_dist_dict[key]< min_color_dist):
            min_color_dist = color_dist_dict[key]
        if(color_dist_dict[key]>max_color_dist):
            max_color_dist = color_dist_dict[key]

    weight_c = 0.3
    weight_g = 1
    
    for key in color_dist_dict:
        norm_color_dist = (color_dist_dict[key]-min_color_dist)/(max_color_dist - min_color_dist)
        #print(norm_color_dist)
        total_dist = weight_c*norm_color_dist + weight_g*dist[index]
        total_dists.append((imgs[key], total_dist))


    total_dists.sort(key=lambda tup: tup[1])
       # with open(db_image_path+"/"+ cur_img_path):
       #     
       # with open(outfile+"/dist.txt","a") as f:
       #     f.write(imgs[index] +": " + str(dist[index])+"\n")
       # img = cv2.imread(db_image_path+"/"+imgs[index])
       # cv2.imwrite(outfile+"/"+imgs[index],im

    nearest_fi_num = 21
    count = 0
    for tup in total_dists:
        if(count >= nearest_fi_num):
            break
        else:    
            with open(outfile+"/dist.txt","a") as f:
                f.write(tup[0]+": " + str(tup[1])+"\n")
            img = cv2.imread("./images_lake"+"/"+tup[0])
            cv2.imwrite(outfile+"/"+tup[0],img)
            count +=1



    #print(imgs[12000])
"""
best_img_filename = ""
best_final_dis = float("inf")
max_dis = 0
for filename in os.listdir(imgdb_dir):
    if filename.endswith(".jpg"): 
        print("Start comparing input image with {}".format(filename))
        img_db_rgb =  cv2.imread(imgdb_dir+filename)
        descriptor_db = gist.extract(img_db_rgb)
        img_db_lab = color.rgb2lab(img_db_rgb)
        img_db_l = img_db_lab[:,:,0]
        img_db_a = img_db_lab[:,:,1]
        img_db_b = img_db_lab[:,:,2]
        #L1 distance between descriptors of input image and  image from db
        des_dis = np.linalg.norm(( descriptor_input- descriptor_db), ord=1)

        if des_dis > max_dis:
            max_dis = des_dis
        print("dis: {}".format(des_dis))
        ssd_l = np.sum((img_db_l - img_input_l)**2)
        ssd_a = np.sum((img_db_a - img_input_a)**2)
        ssd_b = np.sum((img_db_b - img_input_b)**2)
        ssd_avg = (ssd_l + ssd_a + ssd_b)/3
        
        print("ssd_avg: {}".format(ssd_avg))

        
        
print(max_dis)
    
#print(descriptor)

    

"""
