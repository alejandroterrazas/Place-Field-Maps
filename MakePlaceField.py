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

def spike_info_measures(firing_rates, occupancy, overall):
  #overall = np.sum(firing_rates*occupancy)
  info = [p * rate*np.log2(rate/overall) for p,rate in zip(occupancy, firing_rates)]
  info_rate = np.sum([i for i in info if np.isneginf(i) != True and np.isnan(i) != True])
  info_per_spike = info_rate/overall
  return info_rate, info_per_spike

pvdfile = sys.argv[1]
tfilename = sys.argv[2]
mthresh = sys.argv[3]
dsname = sys.argv[4]

animal = dsname.split('/')[0]
recording_date = dsname.split('/')[1].split('_')[0]
recording_time = dsname.split('/')[1].split('_')[1]
cellname=tfilename.replace('./RawData/', '')
outcellname=dsname+'/'+cellname

depth_file = recording_date + ".xlsx"
print("!!!!!!!!!!!!!!!!!!!!!depthfile", depth_file)

if os.path.exists("./RawData/" + depth_file):
  depth_df = pd.read_excel("./RawData/" + depth_file)
  #print("depth_df", depth_df)

  depth_df.drop(depth_df.index[:1])
  depth_df = depth_df.transpose()
 # print("depth_df after transpose", depth_df)

  loc = cellname.find('_')
  trodename = cellname[:loc]
  trodename = trodename.replace('Sc', 'TT') + "-depth"
  depth = depth_df[trodename].values[0]
else:
  depth = -999

print("DEPTH *********", depth)

if os.path.exists('./'+animal+'PFs.xlsx'):
  xl = pd.read_excel('./'+animal+'PFs.xlsx')
else:
  xl = pd.DataFrame(columns = ['cell_name',
                             'moving_rate', 'stopped_rate', 
                             'info/spike', 'info/sec',
                             'moving_spikes', 'stopped_spikes',
                             's1spikes', 's1_fr',
                             'mspikes', 'm_fr',
                             's2spikes', 's2_fr', 'depth'])

ts, x, y = vu.readPVDfile(pvdfile)
x /= 8.2
xsmooth = np.abs(np.convolve(x, np.ones(100, dtype=np.int), 'valid'))/100

#use later to detect direction
direction = np.where(np.diff(xsmooth)>0, 1, 0)

cum = np.cumsum(np.abs(np.diff(xsmooth)))

inotmoving = np.where(np.diff(cum)<.025)[0]
imoving = np.where(np.diff(cum)>=.025)[0]

#linspace args are start, stop, nbins
#bins = np.linspace(25,525,64)/8.2
if animal == '10601':
  print("animal 10601...")
  bins = np.linspace(105,425,64)/8.2

if animal == '10551':
  print("animal 10551...")
  bins = np.linspace(110,425,64)/8.2

if animal == '10604':
  print("animal 10604...")
  bins = np.linspace(110,425,64)/8.2

if animal == '10547':
  print("animal 10547...")
  bins = np.linspace(110,425,64)/8.2

if animal == '10603':
  print("animal 10603...")
  bins = np.linspace(110,425,64)/8.2

if animal == '10608':
  print("animal 10608...")
  bins = np.linspace(110,425,64)/8.2

if animal == '10607':
   print("animal 10607...")
   bins = np.linspace(130,465,64)/8.2
  
occhist, bin_edges = np.histogram(x[imoving],bins=bins)
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

print("Sleep 1 firing rate: {}".format(s1_fr))
print("Maze firing rate: {}".format(m_fr))
print("Sleep 2 firing rate: {}".format(s2_fr))
print('*************')

##segregate spikes in to s1, maze, s2

posx = []
posy = []
stoppedx = []
stoppedy = []

#no need to run time-consuming place analysis on interneurons (>5HZ)

for spike in mspikes:
    closest_t = gu.take_Closest(ts, spike)
    indx, = np.where(ts == closest_t)
    #print("i {}".format(x[i]))
    if indx in imoving:
      posx.append(x[indx])
      posy.append(y[indx])
    else:
      stoppedx.append(x[indx])
      stoppedy.append(y[indx])

fig = plt.figure(figsize=(8,10))
gs = GridSpec(6,4)
gs.update(hspace=0.4, wspace=0.1,left=0.10, right=0.9, top = 0.95, bottom = .1)

ax1 = plt.subplot(gs[:2,:])
#ax1.set_xlim([25,525])

plt.plot(x,y,'r.')
plt.plot(posx,posy, 'b.')
plt.plot([np.min(bins),np.min(bins)], [np.min(posy),np.max(posy)], 'k')
plt.plot([np.max(bins),np.max(bins)], [np.min(posy),np.max(posy)], 'k')


occhist, bin_edges = np.histogram(x[imoving],bins=bins)
occhist = occhist*.016666

moving_time = len(imoving)*.016666
stopped_time = len(inotmoving)*.016666
moving_rate = len(posx)/moving_time
stopped_rate = len(stoppedx)/stopped_time

print('total moving time={}; moving_rate={}'.format(moving_time, moving_rate))
print('total stopped time={}; stopped_rate={}'.format(stopped_time, stopped_rate))

hist, bin_edges = np.histogram(posx,bins=bins)

ax2=plt.subplot(gs[2,:])
  #ax2.set_xlim([25,525])
ax2.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), align='edge')
plt.title('Number of spikes')

ax3=plt.subplot(gs[3,:])
  #ax3.set_xlim([25,525])
ax3.bar(bin_edges[:-1], occhist, width=np.diff(bin_edges), align='edge')
plt.title('Occupancy in seconds')
#plt.show()

corrected=hist/occhist
corrected[np.isnan(corrected)] = 0

ax4=plt.subplot(gs[4,:])
  #ax4.set_xlim([25,525])
ax4.bar(bin_edges[:-1], corrected, width=np.diff(bin_edges), align='edge')
  #print(hist/occhist)
plt.title('Occupancy normalized firing rate')

occpmf, bin_edges = np.histogram(x[imoving],bins=bins, density=True)

  #corrected
info_rate, info_per_spike  = spike_info_measures(corrected, occpmf, moving_rate)

ax5=plt.subplot(gs[5,:])
ax5.text(0.,.9, "Info rate: %3.4f" % info_rate, ha='left', va='center', fontsize=12)
ax5.text(0.,.7, "Info per spike %3.4f" % info_per_spike, ha='left', va='center', fontsize=12)

ax5.text(0.,.5, "Moving firing_rate %3.4f" % moving_rate, ha='left', va='center', fontsize=12)
ax5.text(0.,.3, "Stopped firing_rate %3.4f" % stopped_rate, ha='left', va='center', fontsize=12)

ax5.text(0.5,.9, "animal:  %s" % animal, ha='left', va='center', fontsize=12)
ax5.text(0.5,.7, "date:  %s" % recording_date, ha='left', va='center', fontsize=12)
ax5.text(0.5,.5, "time:  %s" % recording_time.replace('-', ":"), ha='left', va='center', fontsize=12)
ax5.text(0.5,.3, "cell:  %s" % cellname, ha='left', va='center', fontsize=12)
ax5.text(0.5,.1, "depth: %s" % depth, ha='left', va='center', fontsize=12)
ax5.set_axis_off()

mng = plt.get_current_fig_manager()
mng.full_screen_toggle()

tfilename +="PF.png"      
fig.savefig(tfilename, dpi='figure')
plt.close(fig)

xl = xl.append({'cell_name': outcellname, 
                 'moving_rate': moving_rate, 'stopped_rate': stopped_rate,
                 'info/spike': info_per_spike, 'info/sec': info_rate, 
                 'moving_spikes': len(posx), 'stopped_spikes': len(stoppedx),
                 's1spikes': len(s1spikes), 's1_fr': s1_fr,
                 'mspikes': len(mspikes), 'm_fr': m_fr,
                 's2spikes': len(s2spikes), 's2_fr': s2_fr, 'depth': depth}, 
                 ignore_index=True)
print("Appending to XL", xl)
xl.to_excel(animal+'PFs.xlsx')

#plt.show()


