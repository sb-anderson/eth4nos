rm -rf db/db_full
rm -rf db/db_sync
./geth --datadir "./db/db_full" init genesis.json
./geth --datadir "./db/db_sync" init genesis.json
