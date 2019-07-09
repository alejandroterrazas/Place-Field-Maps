import pandas as pd

def readXLSX(fname):
  xl = pd.read_excel(fname)
  pyram = xl.loc[xl['cell_type'] == 'P']
  return pyram

wt = pd.DataFrame(columns =
                 ['cell_name', 'moving_rate', 'stopped_rate', 
                  'info/spike', 'info/sec'])

ko = pd.DataFrame(columns =
                 ['cell_name', 'moving_rate', 'stopped_rate', 
                  'info/spike', 'info/sec'])

WTs = ['10547PFs.xlsx', '10603PFs.xlsx']
KOs = ['10601PFs.xlsx', '10551PFs.xlsx', '10608PFs.xlsx']
                 
for dataset in WTs:
  df = readXLSX(dataset)
  wt = wt.append(df)

for dataset in KOs:
  df = readXLSX(dataset)
  ko = ko.append(df)

##sort by info/spike
wt_sorted = wt.sort_values('info/spike')
ko_sorted = ko.sort_values('info/spike')

print(wt_sorted[['cell_name','info/spike', 'nspikes']])

print(ko_sorted[['cell_name', 'info/spike','nspikes']])

##for each t file in the spreadsheet make a place field map

##add the spike waveform and ISI

##output by rank (e.g.) WT_PF_1.png WT_PF_2.png etc.

##combine into single PDF for WT and KO


