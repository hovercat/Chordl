# Chordl

Chordl is a centralized submission portal for distributed choral singing, currently in development.

The chordlsync tool is already available in the folder [sound_synchronization](/sound_synchronization).

## Sound Synchronization Chordlsync

### Install

These requirements are necessary for chordlsync to run.
- numpy
- scikit-learn
- soundfile
- pandas

You can install them by running:
pip install -r requirements.txt


### Usage
```{sh}
./chordlsync.py PARAMETERS
OR
python chordlsync.py PARAMETERS
```

Usage with default options:
```{sh}
python -m chordlsync -i input_directory -o output_directory
```


All parameters:
```{sh}
./__main__.py -h
usage: __main__.py [-h] -s SYNC_FILE [-o OUTPUT_DIR] -i INPUT_DIR
                              [-f FORMAT] [-j JOBS]
                              [--clip-duration CLIP_DURATION]
                              [--resample-div RESAMPLE_DIV]

Synchronisation für TU Chor Files

optional arguments:
  -h, --help            show this help message and exit
  -s SYNC_FILE, --sync-file SYNC_FILE
                        Synchronization file with beeps in the beginning
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory; default=./out
  -i INPUT_DIR, --input-dir INPUT_DIR
                        Input directory
  -f FORMAT, --format FORMAT
                        Output format; supported are flac and wav; default:
                        flac
  -j JOBS, --jobs JOBS  Number of threads to use; default: 2
  --clip-duration CLIP_DURATION
                        Duration of synchronization to take from every input
                        file; default: 10s
  --resample-div RESAMPLE_DIV
                        Influences the accuracy. The original sample rate is
                        divided by this value for error detection; default: 10
```

Authors:
Kanon G. + Ulrich A.
