
#!/bin/bash

aws s3 cp s3://narp-alext/$1/POSITION/ ./RawData/ --exclude '*' --include '*.
pvd' --include '*.npz' --recursive

pvdname='./RawData/maze_dwPout.pvd' 
#cat $filename | while read line

echo "Getting t files for batch for $line"
#   rm -r -f ./RawData/
dsname="narp-alext/$1"
echo $dsname
aws s3 cp s3://$dsname/ ./RawData/ --recursive --exclude "*" --exclude "*.png" --include "*.t" --include "*.t64" --include "*.ntt" --include "*.xlsx"

for tcellname in ./RawData/*.t*; do
  
     echo "Making placemap for $tcellname"
     python MakeHistograms.py $pvdname $tcellname 0 $1
   
done

