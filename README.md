# :chains:Ethanos

**Ethanos** is a **lightweight Ethereum clients** to accelerate bootstrapping.



## :cactus: ​About repository

The repository has 7 branches including master branch forked from `Geth/v1.9.1-unstable-dad5759a-20190727/linux-amd64/go1.13.4`. Other 6 branches can be separated by clients type and sync mode.

### Clients

* **Ethanos** : Lightweight ethereum client we implemented
* **Geth** : Baseline client for evaluation (Geth/v1.9.1)

### Sync mode

* **Archive node** downloads and replays all the transactions from the genesis block to the current block to reproduce the entire state histories of the blockchain.
* **Fast sync node** downloads all the transactions but replays only the transactions after the pivot block by downloading the pivot block state.
* **Compact sync node** is the same as fast sync except not downloading transactions before the pivot block.



## :globe_with_meridians: Running an archive node

### Environments

* Prerequisite : > go1.10.4
* There are 2 branches for running an archive node.
  * `eth4nos_archive_30`, `geth_archive_30`
* There are some python scripts for simulations in `go-ethereum/build/bin/experiment/`.
  * Please refer to the readme file there

### Setup

In `go-ethereum/build/bin/`,

1. Set `genesis.json` as you want
2. Set `fullDataDir` in `init.sh` 
3. Set `datadir`, `rpcport`, `port` in `full.sh`

### Run

**1. Switch to the target archive branch and build**

```shell
make geth
```

**2. Init client and run**

```shell
sh init.sh
sh full.sh
```

**3. (Optional) Run the simulation script you want in `go-ethereum/build/binexperiment/`**



## :bulb: Running an sync node

### Environments

* Prerequisite : Archive node for syncing
* There are 4 branches for sync experiments.
  * `eth4nos_fast_30`, `eth4nos_compact_30`, `geth_fast_30`, `geth_compact_30`
* There are 3 python scripts for simulations in `go-ethereum/build/bin/sync-experiment/`.
  * `fullnode.py` : Run full(archive) sync node
  * `fastsync.py` : Run fast(or compact) sync node
  * `simulation.py` : Control the execution & termination of full-fast node every epoch

### Setup

1. Genesis file must be the same as archive node's.
2. Set `GENESIS_PATH` and `DB_PATH`(**archive DB path**) in `fullnode.py`
3. Set `GENESIS_PATH` and `DB_PATH`(**where the sync DB will be stored**) in `fastsync.py`
4. Set `DB_PATH`(**where the sync log will be stored**) and `sync_boundaries` in `simulation.py`

### Run

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



## :bar_chart: Analysis

After the sync done,

**1. Move `analysis.sh` in `go-ethereum/build/bin/sync-experiment/` to the log directory**

**2. Run the shell script**

```
sh analysis.sh [fast | compact]
```

* This script assumed that..
  * There are `db_fast/`, `db_compact/` directories in the same location.
  * Log files are named with `*_log/*.txt` pattern in `db_fast/`(or `db_compact/`).
