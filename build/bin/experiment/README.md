how to make eth4nos archive data with 300000 blocks
===================================================

1. set full.sh at ../

    datadir, rpcport, port

2. run geth at ../

    $ sh full.sh

3. set eth4nos_archive_30_simulation.py

    FULL_PORT (same as rpcport at full.sh)

4. run eth4nos_archive_30_simulation.py

    $ python3 eth4nos_archive_30_simulation.py 0 300000
    


how to run yesBloomRstxTest.py & noBloomRstxTest.py
===================================================

yesBloomRstxTest.py
-------------------

1. set full.sh at ../

    datadir, rpcport, port
    
2. run geth at ../

    $ sh full.sh

3. set yesBloomRstxTest.py

    FULL_PORT (same as rpcport at full.sh)
    
4. run yesBloomRstxTest.py 

    $ python3 yesBloomRstxTest.py 
    
    
noBloomRstxTest.py
------------------

1. disable bloom filter at go-ethereum/internal/ethapi/api.go -> GetProof() at line 576

    comment out from line 604 to 635
 
2. remake geth

    $ make geth
 
3. set full.sh at ../

    datadir, rpcport, port
    
4. run geth at ../

    $ sh full.sh

5. set noBloomRstxTest.py

    FULL_PORT (same as rpcport at full.sh)
    
6. run noBloomRstxTest.py 

    $ python3 noBloomRstxTest.py 
    
