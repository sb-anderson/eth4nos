fullDataDir="/data/eth4nos_archive_30_data/db_full"
rm -rf ${fullDataDir}
./geth --datadir ${fullDataDir} init genesis.json
