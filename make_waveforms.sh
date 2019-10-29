
#!/bin/bash

echo "Getting t files for batch for $line"
#   rm -r -f ./RawData/
dsname="narp-alext/$1"
echo $dsname
aws s3 cp s3://$dsname/ ./RawData/ --recursive --exclude "*" --exclude "*.png" --include "*.t" --include "*.t64" --include "*.ntt" --include "*.xlsx"

python ShowAllWaveforms.py

aws s3 cp ./RawData/ s3://$dsname/ --recursive --exclude '*'  --include 'WAVEFORMS*.png'
