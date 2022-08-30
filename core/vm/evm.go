// Copyright 2014 The go-ethereum Authors
// This file is part of the go-ethereum library.
//
// The go-ethereum library is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// The go-ethereum library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.

package vm

import (
	"bytes"
	"math/big"
	"sync/atomic"
	"time"
	"fmt"

	"github.com/eth4nos/go-ethereum/common"
	"github.com/eth4nos/go-ethereum/core/rawdb"
	"github.com/eth4nos/go-ethereum/core/state"
	"github.com/eth4nos/go-ethereum/core/types"
	"github.com/eth4nos/go-ethereum/crypto"
	"github.com/eth4nos/go-ethereum/log"
	"github.com/eth4nos/go-ethereum/params"
	"github.com/eth4nos/go-ethereum/rlp"
	"github.com/eth4nos/go-ethereum/trie"
)

// emptyCodeHash is used by create to ensure deployment is disallowed to already
// deployed contract addresses (relevant after the account abstraction).
var emptyCodeHash = crypto.Keccak256Hash(nil)

type (
	// CanTransferFunc is the signature of a transfer guard function
	CanTransferFunc func(StateDB, common.Address, *big.Int) bool
	// TransferFunc is the signature of a transfer function
	TransferFunc func(StateDB, common.Address, common.Address, *big.Int)
	// RestoreFunc is the signature of a restore function (jmlee)
	RestoreFunc func(StateDB, common.Address, *big.Int, *big.Int)
	// GetHashFunc returns the nth block hash in the blockchain
	// and is used by the BLOCKHASH EVM op code.
	GetHashFunc func(uint64) common.Hash
)

// run runs the given contract and takes care of running precompiles with a fallback to the byte code interpreter.
func run(evm *EVM, contract *Contract, input []byte, readOnly bool) ([]byte, error) {
	if contract.CodeAddr != nil {
		precompiles := PrecompiledContractsHomestead
		if evm.ChainConfig().IsByzantium(evm.BlockNumber) {
			precompiles = PrecompiledContractsByzantium
		}
		if p := precompiles[*contract.CodeAddr]; p != nil {
			return RunPrecompiledContract(p, input, contract)
		}
	}
	for _, interpreter := range evm.interpreters {
		if interpreter.CanRun(contract.Code) {
			if evm.interpreter != interpreter {
				// Ensure that the interpreter pointer is set back
				// to its current value upon return.
				defer func(i Interpreter) {
					evm.interpreter = i
				}(evm.interpreter)
				evm.interpreter = interpreter
			}
			return interpreter.Run(contract, input, readOnly)
		}
	}
	return nil, ErrNoCompatibleInterpreter
}

// Context provides the EVM with auxiliary information. Once provided
// it shouldn't be modified.
type Context struct {
	// CanTransfer returns whether the account contains
	// sufficient ether to transfer the value
	CanTransfer CanTransferFunc
	// Transfer transfers ether from one account to the other
	Transfer TransferFunc
	// Restore restores the inactive account (jmlee)
	Restore RestoreFunc
	// GetHash returns the hash corresponding to n
	GetHash GetHashFunc

	// Message information
	Origin   common.Address // Provides information for ORIGIN
	GasPrice *big.Int       // Provides information for GASPRICE

	// Block information
	Coinbase    common.Address // Provides information for COINBASE
	GasLimit    uint64         // Provides information for GASLIMIT
	BlockNumber *big.Int       // Provides information for NUMBER
	Time        *big.Int       // Provides information for TIME
	Difficulty  *big.Int       // Provides information for DIFFICULTY
}

// EVM is the Ethereum Virtual Machine base object and provides
// the necessary tools to run a contract on the given state with
// the provided context. It should be noted that any error
// generated through any of the calls should be considered a
// revert-state-and-consume-all-gas operation, no checks on
// specific errors should ever be performed. The interpreter makes
// sure that any errors generated are to be considered faulty code.
//
// The EVM should never be reused and is not thread safe.
type EVM struct {
	// Context provides auxiliary blockchain related information
	Context
	// StateDB gives access to the underlying state
	StateDB StateDB
	// Depth is the current call stack
	depth int

	// chainConfig contains information about the current chain
	chainConfig *params.ChainConfig
	// chain rules contains the chain rules for the current epoch
	chainRules params.Rules
	// virtual machine configuration options used to initialise the
	// evm.
	vmConfig Config
	// global (to this context) ethereum virtual machine
	// used throughout the execution of the tx.
	interpreters []Interpreter
	interpreter  Interpreter
	// abort is used to abort the EVM calling operations
	// NOTE: must be set atomically
	abort int32
	// callGasTemp holds the gas available for the current call. This is needed because the
	// available gas is calculated in gasCall* according to the 63/64 rule and later
	// applied in opCall*.
	callGasTemp uint64
}

// NewEVM returns a new EVM. The returned EVM is not thread safe and should
// only ever be used *once*.
func NewEVM(ctx Context, statedb StateDB, chainConfig *params.ChainConfig, vmConfig Config) *EVM {
	evm := &EVM{
		Context:      ctx,
		StateDB:      statedb,
		vmConfig:     vmConfig,
		chainConfig:  chainConfig,
		chainRules:   chainConfig.Rules(ctx.BlockNumber),
		interpreters: make([]Interpreter, 0, 1),
	}

	if chainConfig.IsEWASM(ctx.BlockNumber) {
		// to be implemented by EVM-C and Wagon PRs.
		// if vmConfig.EWASMInterpreter != "" {
		//  extIntOpts := strings.Split(vmConfig.EWASMInterpreter, ":")
		//  path := extIntOpts[0]
		//  options := []string{}
		//  if len(extIntOpts) > 1 {
		//    options = extIntOpts[1..]
		//  }
		//  evm.interpreters = append(evm.interpreters, NewEVMVCInterpreter(evm, vmConfig, options))
		// } else {
		// 	evm.interpreters = append(evm.interpreters, NewEWASMInterpreter(evm, vmConfig))
		// }
		panic("No supported ewasm interpreter yet.")
	}

	// vmConfig.EVMInterpreter will be used by EVM-C, it won't be checked here
	// as we always want to have the built-in EVM as the failover option.
	evm.interpreters = append(evm.interpreters, NewEVMInterpreter(evm, vmConfig))
	evm.interpreter = evm.interpreters[0]

	return evm
}

// Cancel cancels any running EVM operation. This may be called concurrently and
// it's safe to be called multiple times.
func (evm *EVM) Cancel() {
	atomic.StoreInt32(&evm.abort, 1)
}

// Cancelled returns true if Cancel has been called
func (evm *EVM) Cancelled() bool {
	return atomic.LoadInt32(&evm.abort) == 1
}

// Interpreter returns the current interpreter
func (evm *EVM) Interpreter() Interpreter {
	return evm.interpreter
}

// Call executes the contract associated with the addr with the given input as
// parameters. It also handles any necessary value transfer required and takes
// the necessary steps to create accounts and reverses the state in case of an
// execution error or failed value transfer.
func (evm *EVM) Call(caller ContractRef, addr common.Address, input []byte, gas uint64, value *big.Int) (ret []byte, leftOverGas uint64, err error) {
	if evm.vmConfig.NoRecursion && evm.depth > 0 {
		return nil, gas, nil
	}

	// Fail if we're trying to execute above the call depth limit
	if evm.depth > int(params.CallCreateDepth) {
		return nil, gas, ErrDepth
	}
	// Fail if we're trying to transfer more than the available balance
	if !evm.Context.CanTransfer(evm.StateDB, caller.Address(), value) {
		return nil, gas, ErrInsufficientBalance
	}

	var (
		to       = AccountRef(addr)
		snapshot = evm.StateDB.Snapshot()
	)
	if !evm.StateDB.Exist(addr) {
		precompiles := PrecompiledContractsHomestead
		if evm.ChainConfig().IsByzantium(evm.BlockNumber) {
			precompiles = PrecompiledContractsByzantium
		}
		if precompiles[addr] == nil && evm.ChainConfig().IsEIP158(evm.BlockNumber) && value.Sign() == 0 {
			// Calling a non existing account, don't do anything, but ping the tracer
			if evm.vmConfig.Debug && evm.depth == 0 {
				evm.vmConfig.Tracer.CaptureStart(caller.Address(), addr, false, input, gas, value)
				evm.vmConfig.Tracer.CaptureEnd(ret, 0, 0, nil)
			}
			return nil, gas, nil
		}
		evm.StateDB.CreateAccount(addr)
	}

	// old version
	//evm.Transfer(evm.StateDB, caller.Address(), to.Address(), value)
	// new version (jmlee)
	if addr == common.HexToAddress("0x0123456789012345678901234567890123456789") {
		log.Info("\n")

		// TODO: get proof and verify it

		// decode rlp encoded data
		var data []interface{}
		rlp.Decode(bytes.NewReader(input), &data)
		//log.Info("### print input decode", "data", data)

		cnt := 0
		limit := len(data)

		if limit == 0 {
			// Error: no proof in tx data
			log.Info("Restore Error: no proof in tx data")
			return nil, gas, ErrInvalidProof
		}

		// get inactive account address
		inactiveAddrString := string(data[cnt].([]byte))
		inactiveAddr := common.HexToAddress(inactiveAddrString)
		log.Info("### restoration target", "address", inactiveAddr)
		cnt++

		// get block number to start restoration
		startBlockNum := big.NewInt(0)
		startBlockNum.SetBytes(data[cnt].([]byte))
		log.Info("### block num to begin restoration", "start", startBlockNum.Int64())
		cnt++

		// check startBlockNum validity
		mod := big.NewInt(0)
		mod.Mod(startBlockNum, big.NewInt(common.Epoch))
		if mod.Cmp(big.NewInt(common.Epoch-1)) != 0 && startBlockNum.Uint64() != 0 {
			// Error: startBlockNum should be (startBlockNum % epoch == epoch - 1) or just 0
			log.Info("Restore Error: startBlockNum should be checkpoint block number or 0")
			return nil, gas, ErrInvalidProof
		}

		// copy startBlockNum (to iterate blocks)
		blockNum := big.NewInt(0)
		blockNum.SetBytes(data[1].([]byte))

		// set prevAcc, curAcc (to traverse checkpoints' accounts) and resAcc (restored account)
		var prevAcc, curAcc, resAcc *state.Account
		curAcc = nil
		resAcc = &state.Account{}
		resAcc.Balance = big.NewInt(0)

		_, _, _ = prevAcc, curAcc, limit
		//// start here to off restoration proof validation function

		var targetBlocks []uint64
		var accounts []*state.Account
		for cnt < limit {
			// get a bloom filter or a merkle proof from tx data
			targetBlocks = append(targetBlocks, blockNum.Uint64())
			isBloom, stateBloom, merkleProof, blockHeader := parseProof(data, blockNum, &cnt)
			
			// verify proof
			if isBloom {
				// BLOOM
				log.Info("### IS A BLOOM")

				// check existence of the target address
				isExist := stateBloom.TestBytes(inactiveAddr[:])
				if isExist {
					// Error: bloom filter cannot prove the existence of the account
					log.Info("Restore Error: bloom filter said that this account is active")
					return nil, gas, ErrInvalidProof
				} else{
					// there is no account
					accounts = append(accounts, nil)
				}

			} else {
				// NOT A BLOOM
				log.Info("### IS NOT A BLOOM")

				// verify merkle proof
				acc, _, merkleErr := trie.VerifyProof(blockHeader.Root, crypto.Keccak256(inactiveAddr.Bytes()), &merkleProof)
				if merkleErr != nil {
					// bad merkle proof. something is wrong
					log.Info("Restore Error: bad merkle proof")
					return nil, gas, ErrInvalidProof
				}

				if acc == nil {
					// there is no account
					accounts = append(accounts, nil)
				} else {
					// there is the account
					curAcc = &state.Account{}
					rlp.DecodeBytes(acc, &curAcc)
					accounts = append(accounts, curAcc)
				}

			}

		}

		if (evm.BlockNumber.Uint64() < common.Epoch) {
			// Error: cannot restore at epoch 1
			return nil, gas, ErrInvalidProof
		}

		if (blockNum.Uint64() == 0) {
			// receive zero proof -> set blockNum to last checkpoint blockNum
			lastCheckPointBlockNum := evm.BlockNumber.Uint64() - (evm.BlockNumber.Uint64() % common.Epoch) - 1
			blockNum = big.NewInt(int64(lastCheckPointBlockNum))
		}

		// check whether send all proofs except last checkpoint
		if (blockNum.Uint64() + common.Epoch < evm.BlockNumber.Uint64()){

			// Error: not enough proofs
			log.Info("Restore Error: not enough proofs", "blockNum", blockNum.Uint64(), "Epoch", common.Epoch, "evm.BlockNumber", evm.BlockNumber.Uint64())
			return nil, gas, ErrInvalidProof	
		}

		// get target account at last checkpoint
		fmt.Println("Last Checkpoint Block Number: ", blockNum.Uint64())
		targetBlocks = append(targetBlocks, blockNum.Uint64())
		blockHash := rawdb.ReadCanonicalHash(rawdb.GlobalDB, blockNum.Uint64())
		blockHeader := rawdb.ReadHeader(rawdb.GlobalDB, blockHash, blockNum.Uint64())
		cachedState, _ := state.New(blockHeader.Root, evm.StateDB.Database())

		// deal with last checkpoint's account state
		isExist := cachedState.Exist(inactiveAddr)
		if isExist {
			// there is the account
			curAcc = cachedState.GetAccount(inactiveAddr)
			accounts = append(accounts, curAcc)
		} else {
			// there is no account
			accounts = append(accounts, nil)
		}
		

		// accumulate accounts to restore
		log.Info("Restore Info before be compact", "targetBlocks", targetBlocks, "accounts", accounts)

		// 1. pop out useless accounts
		// 1-1. pop nil accounts
		nilAccCnt := 0
		for i := 0; i < len(accounts); i++{
			if accounts[i] != nil {
				break
			}
			nilAccCnt++
		}
		targetBlocks = targetBlocks[nilAccCnt:]
		accounts = accounts[nilAccCnt:]

		log.Info("Restore Info after pop nil acc", "targetBlocks", targetBlocks, "accounts", accounts)

		// 1-2. pop consecutive exist accounts
		if len(accounts) > 1 {
			consecAccCnt := 0
			for i := 1; i < len(accounts); i++{
				if accounts[i] == nil {
					break
				}
				consecAccCnt++
			}
			targetBlocks = targetBlocks[consecAccCnt:]
			accounts = accounts[consecAccCnt:]
		}

		log.Info("Restore Info after pop consec accs", "targetBlocks", targetBlocks, "accounts", accounts)
		
		
		// 2. sum up the balance of accounts
		if len(accounts) == 0 {
			// Error: no accounts to restore (no need to restore)
			log.Info("Restore Error: no accounts to restore")
			return nil, gas, ErrInvalidProof
		}
		accNum := len(accounts)
		accounts = append(accounts, nil) // insert dummy nil account to slide size 2 window
		for i := 0; i < accNum; i++ {
			if accounts[i] != nil && accounts[i+1] == nil {
				log.Info("Restore info", "added acc at block", targetBlocks[i])
				resAcc.Balance.Add(resAcc.Balance, accounts[i].Balance)
			}
			if accounts[i+1] != nil && accounts[i+1].Restored {
				// Error: there is already used account to restore
				log.Info("Restore Error: there is already used account to restore")
				return nil, gas, ErrInvalidProof
			}
		}
		

		//// end here to off restoration proof validation function

		// restore account
		evm.StateDB.CreateAccount(inactiveAddr) // create inactive account to state trie

		log.Info("### Restoration success", "restoredAddr", inactiveAddr, "restoredBalance", resAcc.Balance, "blockNumber", evm.BlockNumber)

		evm.Restore(evm.StateDB, inactiveAddr, resAcc.Balance, evm.BlockNumber) // restore balance

	} else {
		// value transfer tx
		evm.Transfer(evm.StateDB, caller.Address(), to.Address(), value)
	}

	// Initialise a new contract and set the code that is to be used by the EVM.
	// The contract is a scoped environment for this execution context only.
	contract := NewContract(caller, to, value, gas)
	contract.SetCallCode(&addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

	// Even if the account has no code, we need to continue because it might be a precompile
	start := time.Now()

	// Capture the tracer start/end events in debug mode
	if evm.vmConfig.Debug && evm.depth == 0 {
		evm.vmConfig.Tracer.CaptureStart(caller.Address(), addr, false, input, gas, value)

		defer func() { // Lazy evaluation of the parameters
			evm.vmConfig.Tracer.CaptureEnd(ret, gas-contract.Gas, time.Since(start), err)
		}()
	}
	ret, err = run(evm, contract, input, false)

	// When an error was returned by the EVM or when setting the creation code
	// above we revert to the snapshot and consume any gas remaining. Additionally
	// when we're in homestead this also counts for code storage gas errors.
	if err != nil {
		evm.StateDB.RevertToSnapshot(snapshot)
		if err != errExecutionReverted {
			contract.UseGas(contract.Gas)
		}
	}

	if err == nil {
		//log.Info("### at evm.Call(): no error occured") // (jmlee)
	}
	return ret, contract.Gas, err
}

// parseProof get a bloom filter or a merkle proof from tx data
func parseProof(data []interface{}, blockNum *big.Int, cnt *int) (bool, types.StateBloom, state.ProofList, *types.Header) {

	// Get block header
	blockHash := rawdb.ReadCanonicalHash(rawdb.GlobalDB, blockNum.Uint64())
	blockHeader := rawdb.ReadHeader(rawdb.GlobalDB, blockHash, blockNum.Uint64())
	blockNum.Add(blockNum, big.NewInt(common.Epoch))

	// get isBloom from tx data (isBloom -> 0: merkle proof / 1: bloom filter)
	isBloomInt := big.NewInt(0)
	isBloomInt.SetBytes(data[*cnt].([]byte))
	*cnt++
	isBloom := false
	if isBloomInt.Cmp(big.NewInt(1)) == 0 {
		isBloom = true
	}
	// log.Info("### BLOOM", "isbloom", isBloom)

	if isBloom {
		// get bloom filter
		stateBloomBytes, _ := rawdb.ReadBloomFilter(rawdb.GlobalDB, blockHeader.StateBloomHash)
		stateBloom := types.StateBloom{}
		if stateBloomBytes != nil{
			stateBloom = types.BytesToStateBloom(stateBloomBytes)
		}
		
		return isBloom, stateBloom, nil, blockHeader

		// this code is for test, delete this later
		// stateBloom := types.StateBloom{}
		// return isBloom, stateBloom, nil, blockHeader

	} else {
		// get Merkle proof
		merkleProof := make(state.ProofList, 0)
		n := big.NewInt(0)
		n.SetBytes(data[*cnt].([]byte))
		i := big.NewInt(0)
		for ; i.Cmp(n) == -1; i.Add(i, big.NewInt(1)) {
			*cnt++
			pf := data[*cnt].([]byte)
			// log.Info("### print proofs", "proofs", pf)
			merkleProof = append(merkleProof, pf)
		}
		*cnt++

		return isBloom, types.StateBloom{}, merkleProof, blockHeader
	}

}

// CallCode executes the contract associated with the addr with the given input
// as parameters. It also handles any necessary value transfer required and takes
// the necessary steps to create accounts and reverses the state in case of an
// execution error or failed value transfer.
//
// CallCode differs from Call in the sense that it executes the given address'
// code with the caller as context.
func (evm *EVM) CallCode(caller ContractRef, addr common.Address, input []byte, gas uint64, value *big.Int) (ret []byte, leftOverGas uint64, err error) {
	if evm.vmConfig.NoRecursion && evm.depth > 0 {
		return nil, gas, nil
	}

	// Fail if we're trying to execute above the call depth limit
	if evm.depth > int(params.CallCreateDepth) {
		return nil, gas, ErrDepth
	}
	// Fail if we're trying to transfer more than the available balance
	if !evm.CanTransfer(evm.StateDB, caller.Address(), value) {
		return nil, gas, ErrInsufficientBalance
	}

	var (
		snapshot = evm.StateDB.Snapshot()
		to       = AccountRef(caller.Address())
	)
	// Initialise a new contract and set the code that is to be used by the EVM.
	// The contract is a scoped environment for this execution context only.
	contract := NewContract(caller, to, value, gas)
	contract.SetCallCode(&addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

	ret, err = run(evm, contract, input, false)
	if err != nil {
		evm.StateDB.RevertToSnapshot(snapshot)
		if err != errExecutionReverted {
			contract.UseGas(contract.Gas)
		}
	}
	return ret, contract.Gas, err
}

// DelegateCall executes the contract associated with the addr with the given input
// as parameters. It reverses the state in case of an execution error.
//
// DelegateCall differs from CallCode in the sense that it executes the given address'
// code with the caller as context and the caller is set to the caller of the caller.
func (evm *EVM) DelegateCall(caller ContractRef, addr common.Address, input []byte, gas uint64) (ret []byte, leftOverGas uint64, err error) {
	if evm.vmConfig.NoRecursion && evm.depth > 0 {
		return nil, gas, nil
	}
	// Fail if we're trying to execute above the call depth limit
	if evm.depth > int(params.CallCreateDepth) {
		return nil, gas, ErrDepth
	}

	var (
		snapshot = evm.StateDB.Snapshot()
		to       = AccountRef(caller.Address())
	)

	// Initialise a new contract and make initialise the delegate values
	contract := NewContract(caller, to, nil, gas).AsDelegate()
	contract.SetCallCode(&addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

	ret, err = run(evm, contract, input, false)
	if err != nil {
		evm.StateDB.RevertToSnapshot(snapshot)
		if err != errExecutionReverted {
			contract.UseGas(contract.Gas)
		}
	}
	return ret, contract.Gas, err
}

// StaticCall executes the contract associated with the addr with the given input
// as parameters while disallowing any modifications to the state during the call.
// Opcodes that attempt to perform such modifications will result in exceptions
// instead of performing the modifications.
func (evm *EVM) StaticCall(caller ContractRef, addr common.Address, input []byte, gas uint64) (ret []byte, leftOverGas uint64, err error) {
	if evm.vmConfig.NoRecursion && evm.depth > 0 {
		return nil, gas, nil
	}
	// Fail if we're trying to execute above the call depth limit
	if evm.depth > int(params.CallCreateDepth) {
		return nil, gas, ErrDepth
	}

	var (
		to       = AccountRef(addr)
		snapshot = evm.StateDB.Snapshot()
	)
	// Initialise a new contract and set the code that is to be used by the EVM.
	// The contract is a scoped environment for this execution context only.
	contract := NewContract(caller, to, new(big.Int), gas)
	contract.SetCallCode(&addr, evm.StateDB.GetCodeHash(addr), evm.StateDB.GetCode(addr))

	// We do an AddBalance of zero here, just in order to trigger a touch.
	// This doesn't matter on Mainnet, where all empties are gone at the time of Byzantium,
	// but is the correct thing to do and matters on other networks, in tests, and potential
	// future scenarios
	evm.StateDB.AddBalance(addr, bigZero)

	// When an error was returned by the EVM or when setting the creation code
	// above we revert to the snapshot and consume any gas remaining. Additionally
	// when we're in Homestead this also counts for code storage gas errors.
	ret, err = run(evm, contract, input, true)
	if err != nil {
		evm.StateDB.RevertToSnapshot(snapshot)
		if err != errExecutionReverted {
			contract.UseGas(contract.Gas)
		}
	}
	return ret, contract.Gas, err
}

type codeAndHash struct {
	code []byte
	hash common.Hash
}

func (c *codeAndHash) Hash() common.Hash {
	if c.hash == (common.Hash{}) {
		c.hash = crypto.Keccak256Hash(c.code)
	}
	return c.hash
}

// create creates a new contract using code as deployment code.
func (evm *EVM) create(caller ContractRef, codeAndHash *codeAndHash, gas uint64, value *big.Int, address common.Address) ([]byte, common.Address, uint64, error) {
	// Depth check execution. Fail if we're trying to execute above the
	// limit.
	if evm.depth > int(params.CallCreateDepth) {
		return nil, common.Address{}, gas, ErrDepth
	}
	if !evm.CanTransfer(evm.StateDB, caller.Address(), value) {
		return nil, common.Address{}, gas, ErrInsufficientBalance
	}
	nonce := evm.StateDB.GetNonce(caller.Address())
	evm.StateDB.SetNonce(caller.Address(), nonce+1)

	// Ensure there's no existing contract already at the designated address
	contractHash := evm.StateDB.GetCodeHash(address)
	if evm.StateDB.GetNonce(address) != 0 || (contractHash != (common.Hash{}) && contractHash != emptyCodeHash) {
		return nil, common.Address{}, 0, ErrContractAddressCollision
	}
	// Create a new account on the state
	snapshot := evm.StateDB.Snapshot()
	evm.StateDB.CreateAccount(address)
	if evm.ChainConfig().IsEIP158(evm.BlockNumber) {
		evm.StateDB.SetNonce(address, 1)
	}
	evm.Transfer(evm.StateDB, caller.Address(), address, value)

	// Initialise a new contract and set the code that is to be used by the EVM.
	// The contract is a scoped environment for this execution context only.
	contract := NewContract(caller, AccountRef(address), value, gas)
	contract.SetCodeOptionalHash(&address, codeAndHash)

	if evm.vmConfig.NoRecursion && evm.depth > 0 {
		return nil, address, gas, nil
	}

	if evm.vmConfig.Debug && evm.depth == 0 {
		evm.vmConfig.Tracer.CaptureStart(caller.Address(), address, true, codeAndHash.code, gas, value)
	}
	start := time.Now()

	ret, err := run(evm, contract, nil, false)

	// check whether the max code size has been exceeded
	maxCodeSizeExceeded := evm.ChainConfig().IsEIP158(evm.BlockNumber) && len(ret) > params.MaxCodeSize
	// if the contract creation ran successfully and no errors were returned
	// calculate the gas required to store the code. If the code could not
	// be stored due to not enough gas set an error and let it be handled
	// by the error checking condition below.
	if err == nil && !maxCodeSizeExceeded {
		createDataGas := uint64(len(ret)) * params.CreateDataGas
		if contract.UseGas(createDataGas) {
			evm.StateDB.SetCode(address, ret)
		} else {
			err = ErrCodeStoreOutOfGas
		}
	}

	// When an error was returned by the EVM or when setting the creation code
	// above we revert to the snapshot and consume any gas remaining. Additionally
	// when we're in homestead this also counts for code storage gas errors.
	if maxCodeSizeExceeded || (err != nil && (evm.ChainConfig().IsHomestead(evm.BlockNumber) || err != ErrCodeStoreOutOfGas)) {
		evm.StateDB.RevertToSnapshot(snapshot)
		if err != errExecutionReverted {
			contract.UseGas(contract.Gas)
		}
	}
	// Assign err if contract code size exceeds the max while the err is still empty.
	if maxCodeSizeExceeded && err == nil {
		err = errMaxCodeSizeExceeded
	}
	if evm.vmConfig.Debug && evm.depth == 0 {
		evm.vmConfig.Tracer.CaptureEnd(ret, gas-contract.Gas, time.Since(start), err)
	}
	return ret, address, contract.Gas, err

}

// Create creates a new contract using code as deployment code.
func (evm *EVM) Create(caller ContractRef, code []byte, gas uint64, value *big.Int) (ret []byte, contractAddr common.Address, leftOverGas uint64, err error) {
	contractAddr = crypto.CreateAddress(caller.Address(), evm.StateDB.GetNonce(caller.Address()))
	return evm.create(caller, &codeAndHash{code: code}, gas, value, contractAddr)
}

// Create2 creates a new contract using code as deployment code.
//
// The different between Create2 with Create is Create2 uses sha3(0xff ++ msg.sender ++ salt ++ sha3(init_code))[12:]
// instead of the usual sender-and-nonce-hash as the address where the contract is initialized at.
func (evm *EVM) Create2(caller ContractRef, code []byte, gas uint64, endowment *big.Int, salt *big.Int) (ret []byte, contractAddr common.Address, leftOverGas uint64, err error) {
	codeAndHash := &codeAndHash{code: code}
	contractAddr = crypto.CreateAddress2(caller.Address(), common.BigToHash(salt), codeAndHash.Hash().Bytes())
	return evm.create(caller, codeAndHash, gas, endowment, contractAddr)
}

// ChainConfig returns the environment's chain configuration
func (evm *EVM) ChainConfig() *params.ChainConfig { return evm.chainConfig }
