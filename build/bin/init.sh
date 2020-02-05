fullDataDir="/home/jaeykim/data/geth_300000/db_archive"
rm -rf ${fullDataDir}
./geth --datadir ${fullDataDir} init genesis.json
