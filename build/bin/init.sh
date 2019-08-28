fullDataDir="./data/db_full_geth"
rm -rf ${fullDataDir}
./geth --datadir ${fullDataDir} init genesis.json
