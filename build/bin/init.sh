rm -rf db*
./geth --datadir "./db" init genesis.json
./geth --datadir "./db2" init genesis.json
cp keystore/UTC--2019-07-16T04-28-09.643245733Z--bfa1b83f1d20d8c037af4fc66f5fd64287c2c43c db/keystore/
