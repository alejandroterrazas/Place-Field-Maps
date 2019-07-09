
#!/bin/bash
# script to place location firing
rm -r ./PFData/

aws s3 cp s3://narp-alext/$1/NOCURATE ./PFData/TFILES/ --exclude '*' --include 'Sc*.png' --recursive


aws s3 cp s3://narp-alext/$1/PFMAPS ./PFData/PFMAPS/ --exclude '*' --include '*.png' --recursive

#for filename in ./PFData/TFILES/*.png; do
python ./show_pfs_and_tfiles.py
#done

#aws s3 cp s3://narp-alext/$1/ ./RawData/ --exclude '*' --include 'VT1.Nvt' --recursive

#aws s3 cp ./RawData/ s3://narp-alext/$1/PFMAPS --exclude '*' --include '*.png' --recursive


 
