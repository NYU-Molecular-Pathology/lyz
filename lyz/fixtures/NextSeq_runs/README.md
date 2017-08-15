These are empty copies of NextSeq run output directories and files, for use with code validation and testing. 

## Recreate NextSeq Run

Cheatsheet commands to recreate a run for use here (adjust paths for your `pwd` as necessary)

- Copy the directory structure of the run
```bash
rsync -vah --exclude="*.git/*" --include="*/" --exclude="*"  ../../../../quicksilver/170809_NB501073_0019_AH5FFYBGX3 NextSeq_runs/
```

- `touch` copies of needed files

```bash
find 170809_NB501073_0019_AH5FFYBGX3/ -type f ! -name "*.jpg" ! -name "*.bcl*" ! -name "*.fastq*" ! -path "*.git/*" ! -path "*demultiplexing-stats/*" ! -path "*Unaligned/Reports/html/*" ! -path "*InterOp/*" ! -path "*/RTALogs/*" ! -path "*/Recipe/*" ! -path "*/Logs/*" ! -path "*/Config/*" ! -path "*/L00*" ! -path "*old/*" ! -path "*/qsub_logs/*" | while read item; do touch "./lyz/fixtures/NextSeq_runs/${item}"; done
```

- get a list of sample ID's to scrub with [sanitize](https://github.com/stevekm/sanitize/tree/461c1ce0b6150ac45b992bd34cb1723b446cbcd6)

```bash
find lyz/fixtures/NextSeq_runs/170809_NB501073_0019_AH5FFYBGX3/Data/Intensities/BaseCalls/Unaligned/Reports/html/H5FFYBGX3/NS17-16/ -exec basename {} \; | sort -u
# make replace.tsv in Excel
./sanitize_dir-file-link_names.sh ../lyz/fixtures/NextSeq_runs/
```

- copy over the RTA time file
```bash
cp ../170809_NB501073_0019_AH5FFYBGX3/RTAComplete.txt  fixtures/NextSeq_runs/170809_NB501073_0019_AH5FFYBGX3/
```
