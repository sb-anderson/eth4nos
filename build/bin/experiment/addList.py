import json
import numpy as np

# list 1
input_file1 = open('./transactionCountPerBlock_7000001_8000000.json')
txCount = json.load(input_file1)

# list 2
input_file2 = open('./restore_list.json')
rstxCount = json.load(input_file2)

print(len(txCount), len(rstxCount))

# add two lists
addedList = [sum(x) for x in zip(txCount, rstxCount)]
print(len(addedList))
with open("./added_tx_count.json", 'w') as f:
    f.write(json.dumps(addedList))

# pick zero element's index
x = np.array(addedList)
zeroIndices = np.where(x == 0)[0]
zeroIndices = [x+1 for x in zeroIndices]
zeroIndices = list(map(int, zeroIndices))

# save zeroIndices
with open("./zero_tx_block_num.json", 'w') as f:
    f.write(json.dumps(zeroIndices))

