rm -rf db/db*
./geth --datadir "./db/db_full" init genesis.json
./geth --datadir "./db/db_sync" init genesis.json
