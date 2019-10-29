from bisect import bisect_left
import numpy as np
import sys
import struct
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.lines as mlines
import TetrodeUtils as trode
import GeneralUtils as gu
import glob
import scipy.interpolate as interp

def calculate_FWHM(wave_mean):
  '''
  returns the full width, half max points for spike
  '''
  biggest = np.argmax(np.max(wave_mean, axis=1))
  waveform = wave_mean[biggest,:]
  peak = np.argmax(waveform)
  baseline = np.min(waveform[:peak])
  adjusted_waveform = waveform - baseline
  wave_interp_func = interp.interp1d(xvals, adjusted_waveform, kind='linear')
  superx = np.linspace(0,31,100)
  supery = wave_interp_func(superx)
  peak_indx = np.argmax(supery)
  trough_indx = np.argmin(supery)
  prepeak = supery[:peak_indx]
  postpeak = supery[peak_indx:trough_indx]
  half_max = supery[peak_indx]/2
  if len(postpeak) == 0:
    print("empty postpeak")
    FWHM_post = 0
    FWHM_pre = 0
    spike_width = -9
  else:
    FWHM_post = peak_indx + np.argmin(np.abs([val-half_max for val in postpeak]))
    FWHM_pre = np.argmin(np.abs([val-half_max for val in prepeak]))
    spike_width = (FWHM_post - FWHM_pre) * 10
   
  return FWHM_pre, FWHM_post, spike_width


'''
Loop over all tfiles and plot their waveforms
'''
plot_colors = ['b', 'g', 'r', 'c']

#tfiles can have t64 or t as extensions; take either 
tfiles = glob.glob('./RawData/*.t64')
if len(tfiles) == 0:
  tfiles = glob.glob('./RawData/*.t')

#tfiles.append(t64files)
#tfiles = sum(tfiles,[])
print('number of tfiles', len(tfiles))

fig = plt.figure(figsize=(8,10))
#fig = plt.figure()

ncols = np.ceil(np.sqrt(len(tfiles))).astype(int)
nrows = ncols
print("ncols, nrows", ncols, nrows)

gs1 = GridSpec(nrows, ncols)

gs1.update(hspace=0.5, wspace=0.1,
             left=0.1, right=0.95, 
             top = 0.95, bottom = 0.1)

row, col = 0, 0
xvals = range(32)
xtime = [val/31. for val in xvals] 
for tfile in tfiles:

  ttfile=tfile.replace(tfile[tfile.find('_'):], '.ntt')
  ts, waveforms = trode.readTetrode(ttfile)

  spikes = trode.readTFile(tfile)
 
  if len(spikes) > 500:
     spikes = spikes[:500]
 
  smallwave = np.zeros([4,32,len(spikes)])

  ##find the nearest waveform timestamp to tfile timestamp
 
  for indx, spike in enumerate(spikes):
 
    closest = gu.take_Closest(ts, spike*100)
    ts_index = np.where(ts==closest)[0]
   
    smallwave[:,:,indx]=waveforms[:,:,ts_index[0]]
   
  ##computer mean waveform for each channel
  wave_mean = np.zeros([4,32])

  for i in range(4):
     wave_mean[i,:] = np.mean(smallwave[i,:,:], axis=1)

  FWHM_pre, FWHM_post, spike_width = calculate_FWHM(wave_mean)
  print("spike width FWHM: ",spike_width) 
  
  #make the super resolution spike on four channels
  #this allows the FWHM points to be plotted
  super_wave = np.zeros([4,100])
  superx = np.linspace(0,31,100)
  superxtime = [val/31. for val in superx]

  for i in range(4):
     wave_interp_func = interp.interp1d(xvals, wave_mean[i,:], kind='linear')
     super_wave[i,:]  = wave_interp_func(superx)
 
  #plotmin = np.min(wave_mean)
  #plotmax = np.max(wave_mean)
  plotmin = -2000
  plotmax = 2000
  ax = plt.subplot(gs1[row,col])

  for i in range(4):
    plt.plot(superxtime, super_wave[i,:], plot_colors[i])
    plt.ylim([plotmin, plotmax])
 
  biggest = np.argmax(np.max(super_wave, axis=1))
  plt.plot([superxtime[FWHM_pre],superxtime[FWHM_pre]], 
           [plotmin, plotmax], 'k', markersize=4)
  plt.plot([superxtime[FWHM_post],superxtime[FWHM_post]], 
           [plotmin, plotmax], 'k', markersize=4)
  

  ax.set_yticks([])
  infostring = tfile.replace('./RawData/','')
  infostring = infostring.replace('.t64', '')
  infostring = infostring.replace('.t', '')
  infostring = infostring + "  W: " + str(spike_width)
  plt.title(infostring)  
  if col <  ncols-1:
    col += 1
  else:
    col = 0
    row += 1
  
  #ax.axis('off')
  
#plt.show()
mng = plt.get_current_fig_manager()
mng.full_screen_toggle()

fig.savefig("./RawData/WAVEFORMS_NOSCALE.png")
#plt.show()
plt.close(fig)


