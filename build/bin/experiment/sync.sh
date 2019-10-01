rm -rf ../data/sync
../geth --datadir "../data/sync" init "../genesis.json"
../geth --datadir "../data/sync" --syncmode "fast" --networkid 12346 --rpc --rpcport "8085" --rpccorsdomain "*" --port 30306 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --ipcdisable console
