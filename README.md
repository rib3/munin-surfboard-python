# About

[Munin](http://munin-monitoring.org/) plugin
for monitoring Motorola SB6121 cable modems

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

## munin config output
```
./surfboard.sh config
```

# Tests

```
./test.py
```
