# About

[Munin](http://munin-monitoring.org/) plugin
for monitoring Motorola SB6121 cable modems

# Code

Data is scraped from web interface and arranged into objects defined by
`SignalData.parse` in [parse.py](surfboard/parse.py)

Mapping of signal to munin data is defined by `graphs` in [graph.py](surfboard/graph.py)

# Stats

#### downstream
by downstream link
* SNR
* power
* channel
* frequency

#### upstream
by upstream link
* power
* channel
* frequency

#### codeword stats
by downstream link
* unerrored
* correctable
* uncorrectable


# Setup

## TODO easy install setup

## setup/update virtual env

```
./update_env
```

# Running

```
# launch surfboard.py inside virtualenv
./surfboard.sh
```

### with static .htm file

```
./surfboard.sh testdata/working.htm
```

## Munin config

```
./surfboard.sh config
```

### with static .htm file

```
./surfboard.sh config testdata/working.htm
```

# Tests

```
# launch test.py inside virtualenv
./test.sh
```
