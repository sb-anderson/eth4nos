package tests

import (
	"fmt"
	"math/big"

	"github.com/eth4nos/go-ethereum/core/types"
)

func Example1() {

	positive := []string{
		"testtest",
		"test",
		"hallo",
	}

	var bloom types.Bloom
	for _, data := range positive {
		bloom.Add(new(big.Int).SetBytes([]byte(data)))
	}

	fmt.Println("bloom:", bloom)
	fmt.Println("bloom hash:", bloom.Hash().Hex())
	bloom.SetBytes([]byte{1})
	fmt.Println("bloom:", bloom)

	var newBloom types.Bloom
	newBloom.SetBytes([]byte{1})
	fmt.Println("new bloom", newBloom)

	// output: 1
}
