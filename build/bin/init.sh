fullDataDir="/data/db_full"
syncDataDir="/data/db_sync"

rm -rf ${fullDataDir}
rm -rf ${syncDataDir}

if [[ $1 -eq 1 ]]
then
	./geth --datadir ${fullDataDir} init ./genesis/genesis_7000001_7000030.json
	./geth --datadir ${syncDataDir} init ./genesis/genesis_7000001_7000030.json
elif [[ $1 -eq 2 ]]
then
	./geth --datadir ${fullDataDir} init ./genesis/genesis_7000000.json
	./geth --datadir ${syncDataDir} init ./genesis/genesis_7000000.json
else
	./geth --datadir ${fullDataDir} init genesis.json
	./geth --datadir ${syncDataDir} init genesis.json
fi
