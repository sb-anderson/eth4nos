for i in $(seq 1 $1); do
    ./geth account new --datadir . --password password
done
