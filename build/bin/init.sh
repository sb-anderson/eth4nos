fullDataDir="./db/db_full"
rm -rf ${fullDataDir}
./geth --datadir ${fullDataDir} init genesis.json
