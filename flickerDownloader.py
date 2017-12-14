import urllib2
import json
import wget
import urllib
import os
from PIL import Image
from resizeimage import resizeimage
from threading import Thread, Lock
from time import time

def showMessage(m, smutex):
    smutex.acquire()
    print(m)
    smutex.release()

def resize(filename):
     with open(filename, 'r+b') as f:
        with Image.open(f) as image:
           width, height = image.size
           if width < height:
               out = resizeimage.resize_contain(image, [800, 600])
               out.save('./images/{}.jpg'.format(filename[7:-4]), image.format)
           else:
               out = resizeimage.resize_cover(image, [800, 600])
               out.save('./images/{}.jpg'.format(filename[7:-4]), image.format)

def downloader(thread_id, wmutex, rmutex, smutex, task_list):
    while(True):
        rmutex.acquire()
        if (len(task_list)):
            page_idx = task_list.pop()
        else:
            rmutex.release()
            return
        rmutex.release()

        #API KEYs
        api_key = '015f42e7a85ba3ef0c40137cd44fc967'
        api_secret = '9f62050220cddecd'

        error_counter = 0
        invalid_counter = 0
        global download_count

        # for page_idx in range(1,10):
        t1 = time() 
        j_url = ('https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=015f42e7a85ba3ef0c40137cd44fc967&format=json&nojsoncallback=1&text=Chicago&extras=url_o&sort=relevance&page=%d' % (page_idx))
        j_response = urllib2.urlopen(j_url).read()
        j_load = json.loads(j_response)
        j_list = j_load['photos']['photo']
        showMessage('Downloading from page %d, URL = %s' % (page_idx, j_url), smutex)
        num_idx = 0
        for entry in j_list:
            if (not ('url_o' in entry) or (int(entry['height_o']) < 600 or int(entry['width_o']) < 800) or (int(entry['height_o']) > 10000 or int(entry['width_o']) > 10000)): 
                invalid_counter += 1
                continue
            url = entry['url_o']
            try:
                t_open = time()
                f = urllib.urlretrieve(url, 'images/%d_%d.jpg' % (page_idx,num_idx))
                im = Image.open('images/%d_%d.jpg' % (page_idx,num_idx))
                width, height = im.size   
                if width < height:
                   continue
                im_small = im.resize((800, 600), Image.ANTIALIAS)
                im_small.save('images/%d_%d.jpg' % (page_idx,num_idx), im_small.format)
                t_downloaded = time()
                showMessage("Got it %d_%d! In %02f seconds, downloaded by thread %d" % (page_idx, num_idx, (t_downloaded - t_open), thread_id), smutex)
            except Exception, e:
                showMessage('Error occurs when downloading from %s with " %s "' % (url, e), smutex)
                error_counter += 1
            num_idx += 1
        showMessage("Finish downloading & preprocess in thread %d, %d images in this page, %d invalid images, %d errors. In %03f seconds." % (thread_id, num_idx, invalid_counter, error_counter, time()-t1), smutex)
        wmutex.acquire()
        download_count += num_idx
        wmutex.release()

#Run in parallel
if __name__ == '__main__':
    download_count = 0
    task_list = list(range(20)[1:])
    print(task_list)
    wmutex = Lock() 
    rmutex = Lock()
    smutex = Lock()
    tt = time()
    # for page_num in range(1,2):
    #     t = Thread(target = downloader, args = (page_num,wmutex,rmutex,task_list))
    #     t.start()
    for i in range(8):
        print("Init task %d" % i)
        t = Thread(target=downloader, args=(i,wmutex,rmutex,smutex,task_list))
        t.start()
    # for page_num in range(1,2):
    t.join()
    ttt = time()
    print("All finished: Finish downloading %d images in %03f seconds, speed: %02fs/img" % (download_count, ttt-tt, (ttt-tt)/download_count))