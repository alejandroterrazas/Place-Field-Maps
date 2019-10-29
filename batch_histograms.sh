
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
     aws s3 cp s3://$dsname ./RawData/ --exclude "*" --include "*.t" --include "*.t64" --recursive
     aws s3 cp s3://$dsname ./RawData/ --exclude '*' --include 'VT1.Nvt' --recursive
     aws s3 cp s3://$dsname/POSITION ./RawData/ --exclude '*' --include '*' --recursive
     ./make_histograms.sh $line
   fi
done


