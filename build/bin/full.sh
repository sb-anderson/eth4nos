if [ $1 -eq 1 ]
then
  ./geth --datadir "./db" --gcmode archive --networkid 12345 --rpc --rpcport "8877" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./experiment/expScriptInner.js" console
else
    ./geth --datadir "./db" --gcmode archive --networkid 12345 --rpc --rpcport "8877" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock console
fi
