
#!/bin/bash
#this script takes two arguments:
# $1 is a file containing datasets 
# $2 is an output xlsfile file

filename=$1

cat $filename | while read line
do
   echo "Make placefields for batch for $line"
   rm -r -f ./RawData/
   dsname="narp-alext/$line"
   echo $dsname
   if [ "$line" != "" ]; then
     ./make_waveforms.sh $line
   fi
done


