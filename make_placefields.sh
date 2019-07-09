
#!/bin/bash

pvdname='./RawData/maze_dwPout.pvd' 
#cat $filename | while read line

echo "Getting t files for batch for $line"
#   rm -r -f ./RawData/
dsname="narp-alext/$1"
echo $dsname
aws s3 cp s3://$dsname/ ./RawData/ --recursive --exclude "*" --exclude "*.png" --include "*.t" --include "*.t64" --include "*.ntt"

for tcellname in ./RawData/*.t*; do
   asize=$(wc -c <"./MakePFRaster.py")
   if [ $asize -le 300000 ]; then
     echo "Making placemap for $tcellname"
     python MakePlaceField.py $pvdname $tcellname 0 $1
     python MakePFRaster.py $pvdname $tcellname
     python MakeCellSummary.py $tcellname
     convert $tcellname*.png $tcellname.pdf
   fi  
done

aws s3 cp ./RawData/ s3://$dsname/ --recursive --exclude '*' --include '*.pdf' --include '*.png'
