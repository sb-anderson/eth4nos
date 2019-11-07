package tests

import (
	"crypto/rand"
	"encoding/hex"
	"math/big"
	"strconv"

	"github.com/eth4nos/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/common"
)

func randomHex(n int) string {
	bytes := make([]byte, n)
	if _, err := rand.Read(bytes); err != nil {
		return ""
	}
	return hex.EncodeToString(bytes)
}

func Example1() {

	// make empty state bloom
	stateBloom := types.StateBloom{0}

	// account num to insert into bloom
	accNum := 1

	for i := 0; i < accNum; i++ {

		// make address (int to address)
		addr := common.HexToAddress(strconv.Itoa(i))

		// make address (hex to address)
		//addr := common.HexToAddress("0x279a949702698ac715da980aD22951315e7cF490")

		// make address (random)
		// randHex := randomHex(20)
		// randAddr := common.HexToAddress(randHex)

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

	// output: 1
}
