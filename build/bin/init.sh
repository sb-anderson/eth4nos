rm -rf db*
./geth --datadir "./db" init genesis.json
./geth --datadir "./db2" init genesis.json
cp keystore/UTC--2019-07-26T09-16-38.605947084Z--c4422d1c18e9ead8a9bb98eb0d8bb9dbdf2811d7 db/keystore/
