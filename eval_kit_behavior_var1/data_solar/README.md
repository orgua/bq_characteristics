# IVCurves

Measured with shepherds harvester-circuit

```Shell
scp jane@sheep0:/var/shepherd/recordings/LE* ./

shepherd-data extract-meta .

shepherd-data plot -s 1.7998 -e 1.8102 -m .
shepherd-data downsample -s 10 -e 12 --ds-factor 1 .

shepherd-data extract -s 1.80 -e 1.82 --ds-factor 1 .

```
