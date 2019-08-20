package tests

import (
	"fmt"

	"github.com/eth4nos/go-ethereum/common"
)

func Example1() {

	b := []byte("0xc4422d1c18e9ead8a9bb98eb0d8bb9dbdf281777")
	fmt.Println("b:", b)
	s := string(b)
	fmt.Println(s)
	isValidAddress := common.IsHexAddress(s)
	fmt.Println(isValidAddress)

	// output: 1
}
