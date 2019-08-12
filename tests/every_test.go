package tests

import (
	"fmt"
	"time"
)

func Example1() {
	fmt.Println(time.Second)
	time.Sleep(3 * time.Second)
	fmt.Println("test")

	// output: 1
}
