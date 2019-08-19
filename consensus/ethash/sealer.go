// Copyright 2017 The go-ethereum Authors
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

package ethash

import (
	"bytes"
	crand "crypto/rand"
	"encoding/json"
	"errors"
	"math"
	"math/big"
	"math/rand"
	"net/http"
	"runtime"
	"sync"
	"time"

	"github.com/eth4nos/go-ethereum/common"
	"github.com/eth4nos/go-ethereum/common/hexutil"
	"github.com/eth4nos/go-ethereum/consensus"
	"github.com/eth4nos/go-ethereum/core/types"
	"github.com/eth4nos/go-ethereum/log"
)

const (
	// staleThreshold is the maximum depth of the acceptable stale but valid ethash solution.
	staleThreshold = 7
)

var (
	errNoMiningWork      = errors.New("no mining work available yet")
	errInvalidSealResult = errors.New("invalid or stale proof-of-work solution")
	zeroBlocks = []uint64{102,230,310,357,380,433,435,499,754,764,787,1012,1074,1152,1266,1287,1308,1472,1564,1594,1691,1738,1750,1900,1954,1995,2053,2207,2372,2511,2688,2698,3081,3148,3176,3199,3203,3425,4025,4124,4131,4328,4389,4518,4561,4586,4662,4730,4758,4787,4937,5019,5089,5154,5179,5190,5314,5368,5575,5606,5628,5638,5676,5703,5710,5741,5938,5944,6004,6067,6076,6184,6219,6317,6353,6383,6544,6580,6691,6714,7125,7180,7217,7366,7654,7780,7794,7870,7899,7978,8128,8288,8350,8810,8955,9144,9178,9352,9380,10086,10094,10179,10198,10277,10346,10560,10564,10666,10700,10720,10725,10735,10766,10811,10963,11042,11106,11113,11133,11135,11222,11240,11287,11293,11379,11468,11500,11573,11592,11698,11984,12258,12422,12442,12559,12568,12569,12825,12984,13076,13107,13117,13156,13209,13331,13455,13468,13699,13739,13748,13820,14109,14187,14357,14367,14582,14612,14724,14832,14939,14979,15250,15303,15543,15642,15843,15982,16096,16251,16262,16291,16347,16415,16433,16452,16454,16480,16553,16572,16679,16710,16804,16805,16867,16970,17047,17070,17152,17214,17318,17412,17603,17611,17843,17942,18190,18213,18428,18537,18661,18715,18735,18773,18981,19123,19262,19337,19372,19423,19439,19627,19660,19684,19905,19917,20020,20051,20320,20349,20532,20602,20983,21071,21085,21148,21186,21553,21566,21666,21698,21717,21757,21889,21892,21925,21939,21964,22001,22086,22092,22266,22297,22411,22470,22477,22559,22685,22845,22851,22872,22977,23153,23166,23181,23270,23353,23421,23500,23688,23977,24164,24222,24319,24564,25036,25158,25197,25454,25671,25739,25750,25901,25908,25921,26110,26360,26443,26507,26590,26807,26861,26949,26967,26988,27053,27105,27203,27237,27320,27364,27381,27496,27577,27608,27654,27705,27717,27802,27912,27963,28006,28032,28175,28178,28185,28310,28536,28620,28684,28798,28969,29022,29241,29256,29259,29260,29263,29538,29696,29960,30004,30253,30258,30510,30629,30773,31095,31198,31477,31658,31751,31849,31879,31932,32175,32241,32306,32417,32470,32478,32497,32543,32575,32613,32673,32803,32817,32875,33113,33186,33255,33303,33321,33512,33856,33891,33959,33978,34062,34359,34405,34430,34469,34841,34910,35596,35756,35772,36123,36505,36575,36668,36737,36912,37089,37235,37400,37404,37756,37848,38325,38386,38484,38602,38756,38823,38901,39153,39229,39333,39359,39370,39443,39575,39838,39908,40317,40331,40369,40524,40562,40565,40698,40731,40787,40835,41005,41040,41094,41389,41877,42009,42324,42345,42474,42502,42880,42939,43030,43074,43236,43294,43295,43461,43472,43586,43731,43745,43784,43786,43788,43803,43957,44024,44177,44271,44293,44385,44563,44615,44703,44706,44809,44817,44894,44904,44916,44966,45011,45053,45093,45199,45200,45229,45358,45371,45384,45543,45773,45819,45986,46205,46423,46428,46679,46683,46746,47011,47049,47140,47161,47308,47496,47618,47746,47755,47993,48065,48204,48689,48789,48950,48981,49171,49446,49545,49670,49677,49794,49925,50022,50092,50096,50105,50137,50158,50271,50429,50436,50521,50538,50599,50627,50760,50768,50811,50857,50955,51117,51123,51128,51283,51455,51480,51727,51747,51793,51795,52043,52073,52154,52205,52326,52385,52422,52617,52715,52742,52866,53035,53142,53147,53207,53293,53354,53382,53452,53652,53709,54284,54452,54467,54604,54644,54667,54815,54849,54903,54940,54975,54994,55055,55091,55220,55250,55269,55345,55622,55701,55724,55735,55779,55830,55835,56007,56039,56042,56120,56124,56472,56474,56502,56619,56729,56940,56998,57006,57019,57045,57059,57117,57226,57315,57323,57379,57436,57602,57981,58003,58042,58091,58114,58173,58318,58328,58433,58504,58508,58510,58518,58755,58776,58798,58873,58961,59097,59277,59509,59820,60072,60314,60326,60371,60496,60589,60669,60694,60747,60755,60845,60850,60860,60899,60978,61176,61275,61332,61360,61490,61495,61536,61570,61652,61669,61702,61717,61844,61868,61994,62005,62075,62184,62198,62325,62502,62523,62652,62726,62846,62926,62971,63044,63137,63251,63404,63421,63483,63487,63678,63884,64061,64165,64850,65098,65456,65531,65576,65613,65754,65862,65930,65976,65994,66041,66109,66123,66214,66683,66760,67053,67085,67125,67251,67433,67537,67553,67935,67976,68057,68122,68175,68224,68323,68379,68485,68587,68640,68843,69059,69137,69240,69493,69504,69781,69888,69965,70114,70546,70568,70750,70863,71153,71373,71677,71688,72018,72142,72152,72413,72641,72676,72682,72700,72845,72895,72982,73003,73038,73046,73067,73083,73087,73525,73570,73803,73984,74017,74090,74188,74904,74940,75013,75475,75569,75594,76252,76274,76322,76332,76368,76786,76798,76816,77028,77302,77365,77571,77625,77716,77788,77832,77885,78014,78042,78047,78050,78087,78106,78335,78341,78410,78564,78614,78681,78701,78722,78731,78755,78815,78895,78931,79145,79150,79328,79341,79427,79615,79783,79862,79916,80053,80385,80611,81117,81209,81266,81386,81542,81588,81699,81777,81917,82057,82170,82172,82461,82675,82787,82790,82852,82920,82956,83041,83052,83107,83142,83201,83238,83441,83516,83590,83700,83853,83995,84032,84056,84087,84139,84182,84313,84388,84587,85557,85623,85641,85701,85732,85750,85882,85889,86083,86181,86234,86276,86314,86351,86390,86470,86577,86805,86888,86950,86952,87051,87068,87160,87172,87177,87186,87242,87405,87452,87458,87506,87839,87859,87927,88235,88371,88494,88548,88570,88650,88833,88837,88869,88875,88883,88897,88935,88944,88994,89000,89003,89012,89029,89044,89045,89053,89060,89106,89109,89116,89132,89180,89346,89418,89435,89448,89476,89497,89674,89773,89777,89792,89794,89903,90110,90143,90322,90474,90485,90555,90576,90612,90629,90667,90695,90798,91252,91287,91310,91376,91437,91441,91660,91679,91840,91961,92077,92168,92239,92499,92517,92529,92867,92887,92948,93039,93182,93340,93440,93642,93707,93813,93886,94008,94038,94169,94209,94391,94498,94758,94938,94964,95023,95065,95084,95121,95285,95321,95325,95330,95372,95490,95499,95558,95719,95841,95969,95986,96054,96150,96246,96333,96340,96433,96443,96749,96775,97238,97527,97531,97538,97560,97601,97655,97730,97788,97815,97992,98016,98208,98292,98320,98399,98590,98591,98606,98680,98693,98728,98827,98928,98965,99256,99587,99647,99769,99821,99885,99994} // [eth4nos] tx zero block numbers
)

// [eth4nos] lookup slice
func contains(s []uint64, e uint64) bool {
    for _, a := range s {
        if a == e {
            return true
        }
    }
    return false
}

// Seal implements consensus.Engine, attempting to find a nonce that satisfies
// the block's difficulty requirements.
func (ethash *Ethash) Seal(chain consensus.ChainReader, block *types.Block, results chan<- *types.Block, stop <-chan struct{}) error {
	// [eth4nos] If no tx, no sealing @yjkoo
	if len(block.Transactions()) == 0 {
		if !contains(zeroBlocks, block.NumberU64()) {
			log.Info("Sealing paused, waiting for transactions")
			return nil
		}
	}
	// If we're running a fake PoW, simply return a 0 nonce immediately
	if ethash.config.PowMode == ModeFake || ethash.config.PowMode == ModeFullFake {
		header := block.Header()
		header.Nonce, header.MixDigest = types.BlockNonce{}, common.Hash{}
		select {
		case results <- block.WithSeal(header):
		default:
			log.Warn("Sealing result is not read by miner", "mode", "fake", "sealhash", ethash.SealHash(block.Header()))
		}
		return nil
	}
	// If we're running a shared PoW, delegate sealing to it
	if ethash.shared != nil {
		return ethash.shared.Seal(chain, block, results, stop)
	}
	// Create a runner and the multiple search threads it directs
	abort := make(chan struct{})

	ethash.lock.Lock()
	threads := ethash.threads
	if ethash.rand == nil {
		seed, err := crand.Int(crand.Reader, big.NewInt(math.MaxInt64))
		if err != nil {
			ethash.lock.Unlock()
			return err
		}
		ethash.rand = rand.New(rand.NewSource(seed.Int64()))
	}
	ethash.lock.Unlock()
	if threads == 0 {
		threads = runtime.NumCPU()
	}
	if threads < 0 {
		threads = 0 // Allows disabling local mining without extra logic around local/remote
	}
	// Push new work to remote sealer
	if ethash.workCh != nil {
		ethash.workCh <- &sealTask{block: block, results: results}
	}
	var (
		pend   sync.WaitGroup
		locals = make(chan *types.Block)
	)
	for i := 0; i < threads; i++ {
		pend.Add(1)
		go func(id int, nonce uint64) {
			defer pend.Done()
			ethash.mine(block, id, nonce, abort, locals)
		}(i, uint64(ethash.rand.Int63()))
	}
	// Wait until sealing is terminated or a nonce is found
	go func() {
		var result *types.Block
		select {
		case <-stop:
			// Outside abort, stop all miner threads
			close(abort)
		case result = <-locals:
			// One of the threads found a block, abort all others
			select {
			case results <- result:
			default:
				log.Warn("Sealing result is not read by miner", "mode", "local", "sealhash", ethash.SealHash(block.Header()))
			}
			close(abort)
		case <-ethash.update:
			// Thread count was changed on user request, restart
			close(abort)
			if err := ethash.Seal(chain, block, results, stop); err != nil {
				log.Error("Failed to restart sealing after update", "err", err)
			}
		}
		// Wait for all miners to terminate and return the block
		pend.Wait()
	}()
	return nil
}

// mine is the actual proof-of-work miner that searches for a nonce starting from
// seed that results in correct final block difficulty.
func (ethash *Ethash) mine(block *types.Block, id int, seed uint64, abort chan struct{}, found chan *types.Block) {
	// Extract some data from the header
	var (
		header  = block.Header()
		hash    = ethash.SealHash(header).Bytes()
		target  = new(big.Int).Div(two256, header.Difficulty)
		number  = header.Number.Uint64()
		dataset = ethash.dataset(number, false)
	)
	// Start generating random nonces until we abort or find a good one
	var (
		attempts = int64(0)
		nonce    = seed
	)
	logger := log.New("miner", id)
	logger.Trace("Started ethash search for new nonces", "seed", seed)
search:
	for {
		select {
		case <-abort:
			// Mining terminated, update stats and abort
			logger.Trace("Ethash nonce search aborted", "attempts", nonce-seed)
			ethash.hashrate.Mark(attempts)
			break search

		default:
			// We don't have to update hash rate on every nonce, so update after after 2^X nonces
			attempts++
			if (attempts % (1 << 15)) == 0 {
				ethash.hashrate.Mark(attempts)
				attempts = 0
			}
			// Compute the PoW value of this nonce
			digest, result := hashimotoFull(dataset.dataset, hash, nonce)
			if new(big.Int).SetBytes(result).Cmp(target) <= 0 {
				// Correct nonce found, create a new header with it
				header = types.CopyHeader(header)
				header.Nonce = types.EncodeNonce(nonce)
				header.MixDigest = common.BytesToHash(digest)

				// Seal and return a block (if still needed)
				select {
				case found <- block.WithSeal(header):
					logger.Trace("Ethash nonce found and reported", "attempts", nonce-seed, "nonce", nonce)
				case <-abort:
					logger.Trace("Ethash nonce found but discarded", "attempts", nonce-seed, "nonce", nonce)
				}
				break search
			}
			nonce++
		}
	}
	// Datasets are unmapped in a finalizer. Ensure that the dataset stays live
	// during sealing so it's not unmapped while being read.
	runtime.KeepAlive(dataset)
}

// remote is a standalone goroutine to handle remote mining related stuff.
func (ethash *Ethash) remote(notify []string, noverify bool) {
	var (
		works = make(map[common.Hash]*types.Block)
		rates = make(map[common.Hash]hashrate)

		results      chan<- *types.Block
		currentBlock *types.Block
		currentWork  [4]string

		notifyTransport = &http.Transport{}
		notifyClient    = &http.Client{
			Transport: notifyTransport,
			Timeout:   time.Second,
		}
		notifyReqs = make([]*http.Request, len(notify))
	)
	// notifyWork notifies all the specified mining endpoints of the availability of
	// new work to be processed.
	notifyWork := func() {
		work := currentWork
		blob, _ := json.Marshal(work)

		for i, url := range notify {
			// Terminate any previously pending request and create the new work
			if notifyReqs[i] != nil {
				notifyTransport.CancelRequest(notifyReqs[i])
			}
			notifyReqs[i], _ = http.NewRequest("POST", url, bytes.NewReader(blob))
			notifyReqs[i].Header.Set("Content-Type", "application/json")

			// Push the new work concurrently to all the remote nodes
			go func(req *http.Request, url string) {
				res, err := notifyClient.Do(req)
				if err != nil {
					log.Warn("Failed to notify remote miner", "err", err)
				} else {
					log.Trace("Notified remote miner", "miner", url, "hash", log.Lazy{Fn: func() common.Hash { return common.HexToHash(work[0]) }}, "target", work[2])
					res.Body.Close()
				}
			}(notifyReqs[i], url)
		}
	}
	// makeWork creates a work package for external miner.
	//
	// The work package consists of 3 strings:
	//   result[0], 32 bytes hex encoded current block header pow-hash
	//   result[1], 32 bytes hex encoded seed hash used for DAG
	//   result[2], 32 bytes hex encoded boundary condition ("target"), 2^256/difficulty
	//   result[3], hex encoded block number
	makeWork := func(block *types.Block) {
		hash := ethash.SealHash(block.Header())

		currentWork[0] = hash.Hex()
		currentWork[1] = common.BytesToHash(SeedHash(block.NumberU64())).Hex()
		currentWork[2] = common.BytesToHash(new(big.Int).Div(two256, block.Difficulty()).Bytes()).Hex()
		currentWork[3] = hexutil.EncodeBig(block.Number())

		// Trace the seal work fetched by remote sealer.
		currentBlock = block
		works[hash] = block
	}
	// submitWork verifies the submitted pow solution, returning
	// whether the solution was accepted or not (not can be both a bad pow as well as
	// any other error, like no pending work or stale mining result).
	submitWork := func(nonce types.BlockNonce, mixDigest common.Hash, sealhash common.Hash) bool {
		if currentBlock == nil {
			log.Error("Pending work without block", "sealhash", sealhash)
			return false
		}
		// Make sure the work submitted is present
		block := works[sealhash]
		if block == nil {
			log.Warn("Work submitted but none pending", "sealhash", sealhash, "curnumber", currentBlock.NumberU64())
			return false
		}
		// Verify the correctness of submitted result.
		header := block.Header()
		header.Nonce = nonce
		header.MixDigest = mixDigest

		start := time.Now()
		if !noverify {
			if err := ethash.verifySeal(nil, header, true); err != nil {
				log.Warn("Invalid proof-of-work submitted", "sealhash", sealhash, "elapsed", common.PrettyDuration(time.Since(start)), "err", err)
				return false
			}
		}
		// Make sure the result channel is assigned.
		if results == nil {
			log.Warn("Ethash result channel is empty, submitted mining result is rejected")
			return false
		}
		log.Trace("Verified correct proof-of-work", "sealhash", sealhash, "elapsed", common.PrettyDuration(time.Since(start)))

		// Solutions seems to be valid, return to the miner and notify acceptance.
		solution := block.WithSeal(header)

		// The submitted solution is within the scope of acceptance.
		if solution.NumberU64()+staleThreshold > currentBlock.NumberU64() {
			select {
			case results <- solution:
				log.Debug("Work submitted is acceptable", "number", solution.NumberU64(), "sealhash", sealhash, "hash", solution.Hash())
				return true
			default:
				log.Warn("Sealing result is not read by miner", "mode", "remote", "sealhash", sealhash)
				return false
			}
		}
		// The submitted block is too old to accept, drop it.
		log.Warn("Work submitted is too old", "number", solution.NumberU64(), "sealhash", sealhash, "hash", solution.Hash())
		return false
	}

	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case work := <-ethash.workCh:
			// Update current work with new received block.
			// Note same work can be past twice, happens when changing CPU threads.
			results = work.results

			makeWork(work.block)

			// Notify and requested URLs of the new work availability
			notifyWork()

		case work := <-ethash.fetchWorkCh:
			// Return current mining work to remote miner.
			if currentBlock == nil {
				work.errc <- errNoMiningWork
			} else {
				work.res <- currentWork
			}

		case result := <-ethash.submitWorkCh:
			// Verify submitted PoW solution based on maintained mining blocks.
			if submitWork(result.nonce, result.mixDigest, result.hash) {
				result.errc <- nil
			} else {
				result.errc <- errInvalidSealResult
			}

		case result := <-ethash.submitRateCh:
			// Trace remote sealer's hash rate by submitted value.
			rates[result.id] = hashrate{rate: result.rate, ping: time.Now()}
			close(result.done)

		case req := <-ethash.fetchRateCh:
			// Gather all hash rate submitted by remote sealer.
			var total uint64
			for _, rate := range rates {
				// this could overflow
				total += rate.rate
			}
			req <- total

		case <-ticker.C:
			// Clear stale submitted hash rate.
			for id, rate := range rates {
				if time.Since(rate.ping) > 10*time.Second {
					delete(rates, id)
				}
			}
			// Clear stale pending blocks
			if currentBlock != nil {
				for hash, block := range works {
					if block.NumberU64()+staleThreshold <= currentBlock.NumberU64() {
						delete(works, hash)
					}
				}
			}

		case errc := <-ethash.exitCh:
			// Exit remote loop if ethash is closed and return relevant error.
			errc <- nil
			log.Trace("Ethash remote sealer is exiting")
			return
		}
	}
}
