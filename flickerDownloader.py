import urllib2
import json
import urllib
import os
from PIL import Image
from resizeimage import resizeimage
from threading import Thread, Lock
from time import time
import logging

def logMessage(m, status, logger, smutex):
	smutex.acquire()
	if (status == -1):
		logger.error(m)
	else:
		logger.info(m)
	smutex.release()


def showMessage(m, smutex):
	smutex.acquire()
	print(m)
	smutex.release()

def resize(filename):
	 with open(filename, 'r+b') as f:
		with Image.open(f) as image:
			out = resizeimage.resize_cover(image, [800, 600])
			out.save('./images/{}.jpg'.format(filename[7:-4]), image.format)

def downloader(sm, sy, em, ey, thread_id, logger, wmutex, rmutex, smutex, task_list):
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
		j_url = ('https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=015f42e7a85ba3ef0c40137cd44fc967&format=json&nojsoncallback=1&text=lake&extras=url_o&page=%d&sort=relevance&min_upload_date=%d%%2F1%%2F%d&max_upload_date=%d%%2F1%%2F%d' % (page_idx, sm, sy, em, ey))
		j_response = urllib2.urlopen(j_url).read()
		j_load = json.loads(j_response)
		j_list = j_load['photos']['photo']
		showMessage('Downloading from page %d, URL = %s' % (page_idx, j_url), smutex)
		logMessage('Downloading from page %d, URL = %s' % (page_idx, j_url), 1, logger, smutex)
		num_idx = 0
		for entry in j_list:
			if (not ('url_o' in entry) or (int(entry['height_o']) < 600 or int(entry['width_o']) < 800) or (int(entry['height_o']) > 10000 or int(entry['width_o']) > 10000)): 
				invalid_counter += 1
				continue
			url = entry['url_o']
			try:
				t_open = time()
				f = urllib.urlretrieve(url, 'images/%d_%d_%d_%d.jpg' % (sy, sm, page_idx,num_idx))
				im = Image.open('images/%d_%d_%d_%d.jpg' % (sy, sm, page_idx,num_idx)) 

				width, height = im.size   
				if width < height:
					continue
				resize('images/%d_%d_%d_%d.jpg' % (sy, sm, page_idx,num_idx))
				t_downloaded = time()
				num_idx += 1
				# logMessage("Got it %d_%d! In %02f seconds, downloaded by thread %d" % (page_idx, num_idx, (t_downloaded - t_open), thread_id), 1, logger, smutex)
				# showMessage("Got it %d_%d! In %02f seconds, downloaded by thread %d" % (page_idx, num_idx, (t_downloaded - t_open), thread_id), smutex)
			except Exception, e:
				showMessage('Error occurs when downloading from %s with " %s "' % (url, e), smutex)
				logMessage('Error occurs when downloading from %s with " %s "' % (url, e), -1, logger, smutex)
				error_counter += 1
		showMessage("Finish downloading & preprocess in thread %d, %d images in this page, %d invalid images, %d errors. In %03f seconds. Year %d, Month %d." % (thread_id, num_idx, invalid_counter, error_counter, time()-t1, sy, sm), smutex)
		logMessage("Finish downloading & preprocess in thread %d, %d images in this page, %d invalid images, %d errors. In %03f seconds. Year %d, Month %d." % (thread_id, num_idx, invalid_counter, error_counter, time()-t1, sy, sm), 1, logger, smutex)
		wmutex.acquire()
		download_count += num_idx
		wmutex.release()

#Run in parallel
if __name__ == '__main__':
	logger = logging.getLogger('log_file_new')
	hdlr = logging.FileHandler('log_file_new.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.INFO)
	download_count = 0

	task_list = []
	t_start = time()
	for year in range(2004, 2017):
		sy = year
		ey = year
		for month in range(1, 12):
			sm = month
			em = month+1 
			j_url = ('https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=015f42e7a85ba3ef0c40137cd44fc967&format=json&nojsoncallback=1&text=Chicago&extras=url_o&sort=relevance&min_upload_date=%d%%2F1%%2F%d&max_upload_date=%d%%2F1%%2F%d' % (sm,sy,em,ey))
			j_response = urllib2.urlopen(j_url).read()
			j_load = json.loads(j_response)
			j_page = int(j_load['photos']['pages'])
			if (j_page < 40):
				task_list = list(range(j_page+1)[1:])
			else:
				task_list = list(range(41)[1:])
			print(len(task_list))
			if (len(task_list) >= 8):
				k = 8
			else:
				k = len(task_list)
			wmutex = Lock() 
			rmutex = Lock()
			smutex = Lock()
			tt = time()
			for i in range(k):
				print("Init task %d" % i)
				t = Thread(target=downloader, args=(sm, sy, em, ey, i+1, logger, wmutex,rmutex,smutex,task_list))
				t.start()
			# for page_num in range(1,2):
			t.join()
			ttt = time()
			logMessage("Finished: Finish downloading in %03f seconds, Year %d, Month %d" % (ttt-tt, sy, sm), 1, logger, smutex)
			print("Finished: Finish downloading in %03f seconds, Year %d, Month %d" % (ttt-tt, sy, sm))
	t_end = time()
	logMessage("All finished: Finish downloading %d images in %03f seconds, speed: %02fs/img" % (download_count, t_end-t_start, (t_end-t_start)/download_count), 1, logger, smutex)
	print("All finished: Finish downloading %d images in %03f seconds, speed: %02fs/img" % (download_count, t_end-t_start, (t_end-t_start)/download_count))