dataDir="/data/db_full"

if [[ $1 -eq 1 ]]
then
  ./geth --datadir ${dataDir} --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./scripts/script.js" console
elif [[ $1 -eq 2 ]]
then
  ./geth --datadir ${dataDir} --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock --preload "./experiment/expScriptInner.js" console
else
    ./geth --datadir ${dataDir} --keystore "./keystore" --gcmode archive --networkid 12345 --rpc --rpcport "8081" --rpccorsdomain "*" --port 30303 --nodiscover --rpcapi="admin,db,eth,debug,miner,net,shh,txpool,personal,web3" --allow-insecure-unlock console
fi
