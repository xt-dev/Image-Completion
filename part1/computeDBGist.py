import sys
import os
import pickle 
import cv2
import gist
import signal
import numpy as np
from PIL import Image
from threading import Thread, Lock
from time import time
from multiprocessing import Process
import logging
#np.set_printoptions(threshold='nan')

# def restart(range_idx, idx, file_list, imgdb_dir, gist_list, file_dict):

def gist_worker(file_list, imgdb_dir, gist_list, file_dict):
    pid = os.getpid()
    output_gist_file = "./gists_lake_mt"
    output_img_name_pickle_file = "./gists_lake_mt"
    idx = -1
    segfault = 0

    def sig_handler(*args):
        print("=========================================")
        print("Segfault in %d" % pid)
        print("=========================================")
        idx = idx - 1
        segfault = 1

        # restart()
        # os.kill(pid, signal.SIGSEGV)
    
    while(True):
        cur_file = ""
        if (len(file_list) == 0):
            break
        elif (segfault == 0):
            idx = len(file_list)-1
            # if (idx % 100 == 0):
            #     print(idx)
            cur_file = file_list.pop()
        else:
            segfault == 0
        #work on cur_file
        try:     
            # print(cur_file)
            if (idx % 20 == 0):
                print("Computing gist descriptor for %s, index is %d, in process %d" % (cur_file, idx, pid))
            t1 = time()
            # img_rgb = cv2.imread(imgdb_dir+"/"+cur_file)
            img_rgb = Image.open(imgdb_dir+"/"+cur_file)
            descriptor = gist.extract(np.array(img_rgb))
            t2 = time()
            # print("Process time %03f" % (t2-t1))
            #Write to list and dict

            t3 = time()
            gist_list.append(descriptor)
            t4 = time()
            file_dict[idx]=cur_file
            t5 = time()
            # print("Process time1 %03f, time2%03f" % ((t4-t3), (t5-t4)))
            signal.signal(signal.SIGSEGV, sig_handler)
        except Exception, e:
            print("Error occurs in thread %d, file %s, index %d: %s" % (pid, cur_file, idx, e))
        except KeyboardInterrupt:
            print("User break")
            break

    gists = np.array(gist_list)
    np.save(os.path.join(output_gist_file, ("npy_%d.npy" % pid)), gists)
    with open(os.path.join(output_img_name_pickle_file, ("pickle_%d.pickle" % pid)),"wb") as fp:
        pickle.dump(file_dict,fp)
    print("Post-process done")




if __name__ == "__main__":
    imgdb_dir= "./images_lake_small"
    output_gist_file = "./gists_lake_mt"
    output_img_name_pickle_file = "./gists_lake_mt"
    gists = []
    imgs = {}
    global file_list
    file_list = []
    #Set up file list for multi-threading
    for filename in os.listdir(imgdb_dir):
        if filename.endswith(".jpg"): 
            file_list.append(filename)
        else:
            continue
        
    procs = []
    numbers = list(range(100,250))
    print(numbers)

    for index, number in enumerate(numbers):
        proc = Process(target=gist_worker, args=(file_list[1000*number:1000*(number+1)], imgdb_dir, gists, imgs))
        # print("Start %d with range %d to %d" % (pidof(proc), 1000*number, 1000*(number+1)))
        procs.append(proc)
        proc.start()
 
    for proc in procs:
        proc.join()




    # print("Multi-threading working start!")
    # wmutex = Lock() 
    # rmutex = Lock()
    # k = 10
    # for tid in range(k):
    #     print("Init task %d" % tid)
    #     t = Thread(target=gist_worker, args=(tid, imgdb_dir, gists, imgs, rmutex, wmutex))
    #     t.start()
    # t.join()
    # print("Multi-threading finished")
    # gists = np.array(gists)
    # #np.save("gists.npy",gists)
    # np.save(output_gist_file,gists)
    # #with open("imgs.pickle","wb") as fp:
    # with open(output_img_name_pickle_file,"wb") as fp:
    #     pickle.dump(imgs,fp)
    # print("Post-process done")
