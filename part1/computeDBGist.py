import sys
import os
import pickle 
import cv2
import gist
import numpy as np
#np.set_printoptions(threshold='nan')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: python computeDBGist.py imgdb_path output_gist_file output_img_name_pickle_file")
        sys.exit(0)

    #imgdb_dir= "./out/"
    imgdb_dir= sys.argv[1]
    output_gist_file = sys.argv[2]
    output_img_name_pickle_file = sys.argv[3]
    gists = []
    imgs = {}
    count = -1
    for filename in os.listdir(imgdb_dir):
        if filename.endswith(".jpg"): 
            count += 1
        else:
            continue
        if count <= -1:
            continue
        if count > 4000:
            break
        try:     
            print(count)
            print(filename)
            img_rgb = cv2.imread(imgdb_dir+"/"+filename)
            #print("Computing gist descriptor for {}".format(filename))
            
            descriptor = gist.extract(img_rgb)
            #dic[filename] = descriptor
            gists.append(descriptor)
            imgs[count]=filename
                
        except KeyboardInterrupt:
            break
    gists = np.array(gists)
    #np.save("gists.npy",gists)
    np.save(output_gist_file,gists)
    #with open("imgs.pickle","wb") as fp:
    with open(output_img_name_pickle_file,"wb") as fp:
        pickle.dump(imgs,fp)

