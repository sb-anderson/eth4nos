if [ $1 -eq 1 ]
then
  ./geth --datadir "./db/db_full" --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./scripts/script.js" console
elif [ $1 -eq 2 ]
then
  ./geth --datadir "./db/db_full" --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./experiment/expScriptInner.js" console
elif [ $1 -eq 3 ]
then
  ./geth --datadir "./db/db_full_noarchive" --keystore "./keystore" --networkid 12347 --rpc --rpcport "8083" --rpccorsdomain "*" --port 30305 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./experiment/expScriptInner.js" console
else
    ./geth --datadir "./db/db_full" --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock console
fi
