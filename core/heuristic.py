import cv2
import numpy as np
from numpy import asarray
from numpy import savez_compressed
import glob, os
from scipy.spatial import distance
import pickle
import fingerprint_enhancer	

np.warnings.filterwarnings
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

size_of_window = 184
tunning_param = 0.799
rotation = False

def calculateMatching(q_img, t_img, label,rotation):
    akaze = cv2.AKAZE_create()
    sift  = cv2.xfeatures2d.SIFT_create()
    matcher = cv2.DescriptorMatcher_create(4)
    # BFMatcher with default params
    bf = cv2.BFMatcher()
    
 
    crop_img = cv2.imread(q_img,0)
    img = cv2.imread(t_img,0)
    
    best_score = 0
    best_exception_score = 0
    array_data = [500,500,500,500]
    exception_data = [0,0]
    
    array_exception_data = [500,500,500,500]
    image_height = img.shape[0]
    image_width = img.shape[1]
    window_size = size_of_window
    window_step = 64
    
    tmp_img_crop = crop_img


    for i in range(0,image_height, window_step):
        for j in range(0, image_width,window_step):
           
            src_img = img[i:i+window_size, j:j+window_size]
  
            try:
                kpts1= akaze.detect(src_img, None)
                kpts2 = akaze.detect(crop_img, None)


               # compute the descriptors with akaze
                kpts1, desc1 = akaze.compute(src_img, kpts1)
                # compute the descriptors with akaze
                kpts2, desc2 = akaze.compute(crop_img, kpts2)


                nn_matches = matcher.knnMatch(desc1, desc2, 2)
#                 nn_matches = bf.knnMatch(desc1,desc2, k=2)

            

                euclidance_distance = []
                hamming_distance = []
                good = []
                bad = []
                for m,n in nn_matches:
                    
                    if m.distance < tunning_param*n.distance:
                        good.append(m)
                    else:
                        bad.append(m)
               
                if len(good) > exception_data[0] and len(good) <= 5:
                    exception_data = [len(good) ,  0]
                 
                    
                if len(good) > 5 :

                    src_pts = np.float32([ kpts1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                    dst_pts = np.float32([ kpts2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                    hamming_all = [m.distance for m in good]

                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                    matchesMask = mask.ravel().tolist()                 
                    count_good = 0
                    for x in range(0, len(matchesMask)):
                        if matchesMask[x] == 1:
                            euclidance_distance.append( distance.euclidean(src_pts[x], dst_pts[x]) )
                            hamming_distance.append(hamming_all[x])

                    hamming = (sum(hamming_distance) / len(hamming_distance))

                    if len(euclidance_distance) > 0:

                        euclidiance = (sum(euclidance_distance) / len(euclidance_distance))

                        score = len(good)
                        if(best_score < score):   
                            array_data = [hamming, euclidiance, len(good) ,  len(nn_matches)]
                            best_score = score
                            
                    else:
                        euclidiance = 500


                else:
                    score_exception = len(good)
                    if (best_exception_score < score_exception):
                        src_pts = np.float32([ kpts1[m.queryIdx].pt for m in bad ]).reshape(-1,1,2)
                        dst_pts = np.float32([ kpts2[m.trainIdx].pt for m in bad ]).reshape(-1,1,2)
                        hamming_all = [m.distance for m in bad]

                        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                        matchesMask = mask.ravel().tolist()                 

                        for x in range(0, len(matchesMask)):
                            if matchesMask[x] == 1:
                                euclidance_distance.append( distance.euclidean(src_pts[x], dst_pts[x]) )
                                hamming_distance.append(hamming_all[x])
                        if len(euclidance_distance) > 0:
                            hamming = (sum(hamming_distance) / len(hamming_distance))
                            euclidiance = (sum(euclidance_distance) / len(euclidance_distance))


                        array_exception_data = [hamming, euclidiance, score_exception ,  len(nn_matches)]
                        best_exception_score = score_exception
                      
                        

            except:
                exception_data = [500,500]
              
   
  
        
    if array_data[2] == 500 and array_data[3] == 500:
        if exception_data[0] == 500:
            exception_data[0] = 0
            exception_data[1] = 0
        array_data[2] = exception_data[0]
        array_data[3] = exception_data[1]
        if array_data[2] >= 40:
            array_data[2] = 0
        else:
            array_data[2] = 40 - array_data[2]

        return 500, np.array(array_data)
    else:
        if array_data[2] >= 40:
            array_data[2] = 0
        else:
            array_data[2] = 40 - array_data[2]
       
        return 0,  np.array(array_data)