import numpy as np
from matplotlib import pyplot as plt
import os
import sys
import pandas as pd
import TetrodeUtils as tu
import GeneralUtils as gu
import VideoUtils as vu
from matplotlib.gridspec import GridSpec
from scipy.stats import entropy
import scipy.stats as stats

pvdfile = sys.argv[1]
tfilename = sys.argv[2]
mthresh = sys.argv[3]
dsname = sys.argv[4]

animal = dsname.split('/')[0]
recording_date = dsname.split('/')[1].split('_')[0]
recording_time = dsname.split('/')[1].split('_')[1]
cellname=tfilename.replace('./RawData/', '')
outcellname=dsname+'/'+cellname

ts, x, y = vu.readPVDfile(pvdfile)
x /= 8.2
xsmooth = np.abs(np.convolve(x, np.ones(100, dtype=np.int), 'valid'))/100

#use later to detect direction
direction = np.where(np.diff(xsmooth)>0, 1, 0)
#print("size of direction: ", np.size(direction))
#inotmoving and imoving are for entire recording
cum = np.cumsum(np.abs(np.diff(xsmooth)))

inotmoving = np.where(np.diff(cum)<.025)[0]
imoving = np.where(np.diff(cum)>=.025)[0]

print("reation")
print(np.size(inotmoving))
print(np.size(imoving))


#imaze = np.hstack([imoving, inotmoving])


imoving_left, imoving_right = [], []

for indx in imoving:
   if direction[indx]== 0:
     imoving_left.append(indx)
   elif direction[indx] == 1:
     imoving_right.append(indx)


#linspace args are start, stop, nbins
#bins = np.linspace(25,525,64)/8.2

if animal == '10607':
  bins = np.linspace(130, 465, 64)/8.2
else:
  bins = np.linspace(110,425,64)/8.2

 
print(tfilename)
vts,_,_,_,_ = vu.getVideoData('./RawData/VT1.Nvt')
vts /= 100

spikes = tu.readTFile(tfilename)

print("spikes[0] {}, spikes[-1] {}".format(spikes[0], spikes[-1]))
print("ts[0] {}, ts[-1] {}".format(ts[0], ts[-1]))

npzfile = np.load('./RawData/EPOCHS.npz')
start = npzfile['arr_0'].astype(int)
stop = npzfile['arr_1'].astype(int)

s1spikes = [spike for spike in spikes if vts[0]<spike<vts[start]]
mspikes = [spike for spike in spikes if vts[start]<spike<vts[stop]]
s2spikes = [spike for spike in spikes if vts[stop]<spike<vts[-1]]

s1_fr = len(s1spikes)/((vts[start]-vts[0])/10000)
m_fr = len(mspikes)/((vts[stop]-vts[start])/10000)
s2_fr = len(s2spikes)/((vts[-1]-vts[stop])/10000)

##segregate spikes in to s1, maze, s2

posx_left = []
posy_left = []

posx_right = []
posy_right = []

#no need to run time-consuming place analysis on interneurons (>5HZ)

for spike in mspikes:
    closest_t = gu.take_Closest(ts, spike)
    indx, = np.where(ts == closest_t)
    #print("i {}".format(x[i]))
    if indx in imoving:
      if direction[indx] == 0:
         posx_left.append(x[indx])
         posy_left.append(y[indx])
      else:
         posx_right.append(x[indx])
         posy_right.append(x[indx])


occhist_left, _ = np.histogram(x[imoving_left],bins=bins)
occhist_right, _ = np.histogram(x[imoving_right],bins=bins)
occhist_left = occhist_left*.016666
occhist_right = occhist_right*.016666

occpmf_left, _  = np.histogram(x[imoving_left], bins=bins, density=True)
occpmf_right, _ = np.histogram(x[imoving_right], bins=bins, density=True)
#occpmf_left, _  = np.histogram(x[imoving_left], bins=bins)
#occpmf_right, _ = np.histogram(x[imoving_right], bins=bins)

moving_rate_left = len(posx_left)/(len(imoving_left)*0.016666)
moving_rate_right = len(posx_right)/(len(imoving_right)*0.01666)

hist_left, _  = np.histogram(posx_left,bins=bins)
hist_right, _  = np.histogram(posx_right,bins=bins)


#occupancy corrected histogram
corrected_left=hist_left/occhist_left
corrected_right=hist_right/occhist_right
corrected_left[np.isnan(corrected_left)] = 0
corrected_right[np.isnan(corrected_right)] = 0

outfile = './' + animal + 'HISTODATA.npz'
#print("corrected: ", type(corrected_left))
#print("occpmf: ", np.shape(occpmf_left))
#print("moving: ", type(moving_rate_left))

if os.path.exists(outfile):
   npzfile = np.load(outfile)   

   npz_hist_left = npzfile['corrected_left']
   npz_hist_left = np.vstack([npz_hist_left, corrected_left])

   npz_occpmf_left = npzfile['occpmf_left']
   npz_occpmf_left = np.vstack([npz_occpmf_left, occpmf_left])

   npz_moving_rate_left = npzfile['moving_rate_left']
   npz_moving_rate_left = np.vstack([npz_moving_rate_left, moving_rate_left])

   npz_hist_right = npzfile['corrected_right']
   npz_hist_right = np.vstack([npz_hist_right, corrected_right])

   npz_occpmf_right = npzfile['occpmf_right']
   npz_occpmf_right = np.vstack([npz_occpmf_right, occpmf_right])

   npz_moving_rate_right = npzfile['moving_rate_right']
   npz_moving_rate_right = np.vstack([npz_moving_rate_right, moving_rate_right])

   npz_cellname = npzfile['cell_name']
   npz_cellname = np.vstack([npz_cellname, outcellname])

   np.savez(outfile, 
            corrected_left=npz_hist_left,
            occpmf_left=npz_occpmf_left,
            moving_rate_left=npz_moving_rate_left,  
            corrected_right=npz_hist_right,
            occpmf_right=npz_occpmf_right,
            moving_rate_right=npz_moving_rate_right,
            cell_name=npz_cellname)
else:
   np.savez(outfile, 
            corrected_left=corrected_left,
            occpmf_left=occpmf_left,
            moving_rate_left=moving_rate_left,
            corrected_right=corrected_right,
            occpmf_right=occpmf_right,
            moving_rate_right=moving_rate_right,
            cell_name=outcellname)

