package tests

import (
	"math/big"
	"strconv"

	"github.com/eth4nos/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/common"
)

func Example1() {

	// make empty state bloom
	stateBloom := types.StateBloom{0}

	// account num to insert into bloom
	accNum := 500

	for i := 0; i < accNum; i++ {

		// make address
		addr := common.HexToAddress(strconv.Itoa(i)) // int to address
		//addr := common.HexToAddress("0x279a949702698ac715da980aD22951315e7cF490")	// hex to address

		// insert into bloom
		stateBloom.Add(new(big.Int).SetBytes(addr[:]))

	}

	for i := accNum; i < 2*accNum; i++ {

		addr := common.HexToAddress(strconv.Itoa(i))

		// check if there is address or not (it can be false positive answer)
		isExist := stateBloom.TestBytes(addr[:])

		if isExist {
			println("i: ", i, " / address: ", addr.Hex(), "isExist: ", isExist)
		}
	}

	// blockNum := big.NewInt(345599)
	// blockHash := rawdb.ReadCanonicalHash(rawdb.GlobalDB, blockNum.Uint64())
	// blockHeader := rawdb.ReadHeader(rawdb.GlobalDB, blockHash, blockNum.Uint64())
	// stateBloomBytes, _ := rawdb.ReadBloomFilter(rawdb.GlobalDB, blockHeader.StateBloomHash)
	// stateBloom := types.BytesToStateBloom(stateBloomBytes)
	// addr := common.HexToAddress("0x279a949702698ac715da980aD22951315e7cF490")
	// stateBloom.Add(new(big.Int).SetBytes(addr[:]))

	// output: 1
}
