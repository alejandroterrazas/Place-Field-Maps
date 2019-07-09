#!/usr/bin/env python
# coding: utf-8

# In[5]:



from bisect import bisect_left
import numpy as np
import sys
import struct
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.lines as mlines
import TetrodeUtils as trode
import GeneralUtils as gu

def autocor(x,t):
   return np.corrcoef(x[0:len(x)-t], x[t:len(x)])[0,1]
   #for l in range(len(x)):
   #   print(x[l])

tfile=sys.argv[1]
#ttfile=sys.argv[2]
ttfile=tfile.replace(tfile[tfile.find('_'):],'.ntt')

print("Making Cell Plot for files: {}".format(tfile))


# In[6]:


ts, waveforms = trode.readTetrode(ttfile)
if len(ts) > 1000000:
   sys.exit()

print(len(ts))
spikes = trode.readTFile(tfile)

totaltime = (ts[-1] - ts[0])/600000
print("totaltime: {}".format(totaltime/100.))


# In[7]:


fig = plt.figure(figsize=(8,10))
#fig = plt.figure()

gs1 = GridSpec(3,4)
gs1.update(hspace=0.4, wspace=0.1,
             left=0.10, right=0.48, 
             top = 0.95, bottom = 0.3)
   
gs2 = GridSpec(3,3)
gs2.update(left=0.58, right=.98, 
           top = 0.95, bottom = 0.3, wspace=0.05)

gs3 = GridSpec(1,1)
gs3.update(left=0.10, right=.98, 
           top=.2, bottom = 0.05, wspace=0.05)


# In[8]:



smallwave = np.zeros([4,32,len(spikes)])

print("Number of spikes {}".format(len(spikes)))
print("Firing Rate {}".format(len(spikes)/totaltime))


##find the nearest waveform timestamp to tfile timestamp
for indx, spike in enumerate(spikes):
   #print(spike*60)
   closest = gu.take_Closest(ts, spike*100)
   ts_index = np.where(ts==closest)[0]
   
   smallwave[:,:,indx]=waveforms[:,:,ts_index[0]]

#compute spike statistics
wave_std = np.zeros([4,32])
wave_mean = np.zeros([4,32])

for i in range(4):
 wave_mean[i,:] = np.mean(smallwave[i,:,:], axis=1)
 for j in range(32):
     wave_std[i,:] = np.std(smallwave[i,j,:])

#plt.plot(wave_mean)
#plt.show()


# In[47]:


isi = np.log10(np.where(np.diff(spikes)>0, np.diff(spikes/1000), 1e-15))
binvals = [5*i/5000. for i in range(5000)]
isi[np.isinf(isi)] = 0

n_noise = len(np.where(np.diff(spikes/1000.) <= 2))
print("# spikes less than 2 ms: {}".format(n_noise))
hisi, bin_edges = np.histogram(isi)

ax1 = plt.subplot(gs1[:-1, :])
#ax1.set_autoscaley_on(False)
#ax1.set_xlim([2,10])
ax1 = plt.bar(bin_edges[:-1], hisi, 0.3)
plt.ylabel('# of spikes')
plt.xlabel('Log10 interspike interval')
locs, labs = plt.xticks()

for lab,loc in zip(labs,locs):
    lab.set_text("$10^{0}$".format(loc.astype(int)))
       
plt.xticks(locs[1:-1], labs[1:-1])

#compute spike statistics

plot_colors = ['b', 'g', 'r', 'c']
     

#ax.set_autoscaley_on(False)
#ax.set_ylim([amin-100,amax+100])
   
#ax.text(32,amplimax[i],"{}".
#        format(amplimax[i].astype(int)),ha='right', va='top') 

#put the tetrode spike waveforms on the page
plotmax = np.max(wave_mean)
plotmin = np.min(wave_mean)

for i in range(4):
    ax = plt.subplot(gs1[-1,i])
    plt.plot(wave_mean[i,:], plot_colors[i])
    plt.ylim([plotmin, plotmax])
#   plt.plot([0,32],[amplimax[i],amplimax[i]],'k')

ax6 = plt.subplot(gs2[0, :])
  
max_index=np.where(wave_mean[0,:]==np.max(wave_mean[0,:]))[0]
max_index = max_index[0] 

 
ax6.text(0,.9,"Number of spikes: {}".
         format(len(spikes)), ha='left', va='center', fontsize=12)

ax6.text(0,.5,"Firing Rate: %3.2f Hz" % (len(spikes)/totaltime), 
         ha='left', va='center',fontsize=12)

ax6.text(0,.2,"Total Time: %3.2f minutes" % (totaltime/100.),
         ha='left', va='center', fontsize=12)

ax6.set_axis_off()

   
ax7 = plt.subplot(gs2[-1, :])
spikes_ms = spikes/24000
spikes_ms = spikes_ms - spikes_ms[0]

spike_bins = np.zeros(spikes_ms[-1].astype(int)+1)
spike_bins[spikes_ms.astype(int)] = 1
auto_correlogram=np.zeros(250)
for k in range(250):
    auto_correlogram[k] = autocor(spike_bins,k)
     
plt.plot(auto_correlogram[1:], 'k-')


# In[43]:



#ax8 = plt.subplot(gs3[0,:])
#spikes_m = (spikes-ts[0])/36000000
#plot_dotcolors = ['b.','g.','r.', 'c.']

#for i in range(4):
#   #plt.plot(spikes_m, peaks[i,:], plot_dotcolors[i], markersize=1)
#   plt.plot([0, spikes_m[-1]],
#             [amplimax[i],amplimax[i]],plot_colors[i], linewidth=2)


#   locs, labs = plt.xticks()
  
#   for lab,loc in zip(labs,locs):
#        lab.set_text("{}".format(loc))

#   plt.xticks(locs[1:-1], labs[1:-1])


# In[2]:


mng = plt.get_current_fig_manager()
mng.full_screen_toggle()
print("writing cell summary file: " + tfile + "CS.png")

fig.savefig(tfile+"CS.png")
#plt.show()
plt.close(fig)



# In[ ]:




