# MLB - Missed Calls Bot

## Steps

1. Download Statcast Data for previous day
2. Restrict data to balls & called strikes
3. Pass to analysis .py to calculate miss
   - Sampling to determine typical misses
   - Horizontal / vertical misses
4. Download clips of each play from the MLB Video Room
5. Stitch videos together into a compilation

## Packages

- Pandas
- Tqdm
- Moviepy
