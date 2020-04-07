# :chains:Ethanos
## :bulb:Sync Experiment
### :file_folder:Environments
* Prerequisite : Archive DB for Ethanos(or Geth)
* There are 4 branches for sync experiments.
  * `eth4nos_fast_30`, `eth4nos_compact_30`, `geth_fast_30`, `geth_compact_30`
* There are 3 python scripts for simulations in `go-ethereum/build/bin/sync-experiment/`.
  * `fullnode.py` : Run full(archive) sync node
  * `fastsync.py` : Run fast(or compact) sync node
  * `simulation.py` : Control the execution & termination of full-fast node every epoch

### :computer:Setup
1. Set `GENESIS_PATH` and `DB_PATH`(**archive DB path**) in `fullnode.py`
2. Set `GENESIS_PATH` and `DB_PATH`(**where the sync DB will be stored**) in `fastsync.py`
2. Set `DB_PATH`(**where the sync log will be stored**) and `sync_boundaries` in `simulation.py`

### :woman_technologist:Run
**1. Switch to the target sync branch and build**
```shell
make geth
```
**2. (Optional) Start 3 new screen sessions**
```shell
screen -S full
screen -S sync
screen -S simulation
```
**3. Run `fullnode.py` in `full` session**
```
python3 fullnode.py
```
**4. Run `fastsync.py` in `sync` session**
```
python3 fastsync.py
```
**5. Run `simulation.py` in `simulation` session with 2 arguments**
```
python3 simulation.py [directory prefix] [# of sync in each epoch]
```

### :bar_chart:Analysis
**1. Move `analysis.sh` in `go-ethereum/build/bin/sync-experiment/` to the log directory**

**2. Run the shell script**
```
sh analysis.sh [fast | compact]
```
* This script assumed that..
  * There are `db_fast/`, `db_compact/` directories in the same location.
  * Log files are named with `*_log/*.txt` pattern in `db_fast/`(or `db_compact/`).
