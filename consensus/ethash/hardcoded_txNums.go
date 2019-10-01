package ethash

var (
	// TxNums is hardcoded tx per block (block 7,000,001 ~ 7,300,000) (epoch: 40320)
	ZeroBlocks = []uint64{102, 230, 310, 357, 380, 433, 435, 499, 754, 764, 787, 1012, 1074, 1152, 1266, 1287, 1308, 1472, 1564, 1594, 1691, 1738, 1750, 1900, 1954, 1995, 2053, 2207, 2372, 2511, 2688, 2698, 3081, 3148, 3176, 3199, 3203, 3425, 4025, 4124, 4131, 4328, 4389, 4518, 4561, 4586, 4662, 4730, 4758, 4787, 4937, 5019, 5089, 5154, 5179, 5190, 5314, 5368, 5575, 5606, 5628, 5638, 5676, 5703, 5710, 5741, 5938, 5944, 6004, 6067, 6076, 6184, 6219, 6317, 6353, 6383, 6544, 6580, 6691, 6714, 7125, 7180, 7217, 7366, 7654, 7780, 7794, 7870, 7899, 7978, 8128, 8288, 8350, 8810, 8955, 9144, 9178, 9352, 9380, 10086, 10094, 10179, 10198, 10277, 10346, 10560, 10564, 10666, 10700, 10720, 10725, 10735, 10766, 10811, 10963, 11042, 11106, 11113, 11133, 11135, 11222, 11240, 11287, 11293, 11379, 11468, 11500, 11573, 11592, 11698, 11984, 12258, 12422, 12442, 12559, 12568, 12569, 12825, 12984, 13076, 13107, 13117, 13156, 13209, 13331, 13455, 13468, 13699, 13739, 13748, 13820, 14109, 14187, 14357, 14367, 14582, 14612, 14724, 14832, 14939, 14979, 15250, 15303, 15543, 15642, 15843, 15982, 16096, 16251, 16262, 16291, 16347, 16415, 16433, 16452, 16454, 16480, 16553, 16572, 16679, 16710, 16804, 16805, 16867, 16970, 17047, 17070, 17152, 17214, 17318, 17412, 17603, 17611, 17843, 17942, 18190, 18213, 18428, 18537, 18661, 18715, 18735, 18773, 18981, 19123, 19262, 19337, 19372, 19423, 19439, 19627, 19660, 19684, 19905, 19917, 20020, 20051, 20320, 20349, 20532, 20602, 20983, 21071, 21085, 21148, 21186, 21553, 21566, 21666, 21698, 21717, 21757, 21889, 21892, 21925, 21939, 21964, 22001, 22086, 22092, 22266, 22297, 22411, 22470, 22477, 22559, 22685, 22845, 22851, 22872, 22977, 23153, 23166, 23181, 23270, 23353, 23421, 23500, 23688, 23977, 24164, 24222, 24319, 24564, 25036, 25158, 25197, 25454, 25671, 25739, 25750, 25901, 25908, 25921, 26110, 26360, 26443, 26507, 26590, 26807, 26861, 26949, 26967, 26988, 27053, 27105, 27203, 27237, 27320, 27364, 27381, 27496, 27577, 27608, 27654, 27705, 27717, 27802, 27912, 27963, 28006, 28032, 28175, 28178, 28185, 28310, 28536, 28620, 28684, 28798, 28969, 29022, 29241, 29256, 29259, 29260, 29263, 29538, 29696, 29960, 30004, 30253, 30258, 30510, 30629, 30773, 31095, 31198, 31477, 31658, 31751, 31849, 31879, 31932, 32175, 32241, 32306, 32417, 32470, 32478, 32497, 32543, 32575, 32613, 32673, 32803, 32817, 32875, 33113, 33186, 33255, 33303, 33321, 33512, 33856, 33891, 33959, 33978, 34062, 34359, 34405, 34430, 34469, 34841, 34910, 35596, 35756, 35772, 36123, 36505, 36575, 36668, 36737, 36912, 37089, 37235, 37400, 37404, 37756, 37848, 38325, 38386, 38484, 38602, 38756, 38823, 38901, 39153, 39229, 39333, 39359, 39370, 39443, 39575, 39838, 39908, 40317, 40331, 40369, 40524, 40562, 40565, 40698, 40731, 40787, 40835, 41005, 41040, 41094, 41389, 41877, 42009, 42324, 42345, 42474, 42502, 42880, 42939, 43030, 43074, 43236, 43294, 43295, 43461, 43472, 43586, 43731, 43745, 43784, 43786, 43788, 43803, 43957, 44024, 44177, 44271, 44293, 44385, 44563, 44615, 44703, 44706, 44809, 44817, 44894, 44904, 44916, 44966, 45011, 45053, 45093, 45199, 45200, 45229, 45358, 45371, 45384, 45543, 45773, 45819, 45986, 46205, 46423, 46428, 46679, 46683, 46746, 47011, 47049, 47140, 47161, 47308, 47496, 47618, 47746, 47755, 47993, 48065, 48204, 48689, 48789, 48950, 48981, 49171, 49446, 49545, 49670, 49677, 49794, 49925, 50022, 50092, 50096, 50105, 50137, 50158, 50271, 50429, 50436, 50521, 50538, 50599, 50627, 50760, 50768, 50811, 50857, 50955, 51117, 51123, 51128, 51283, 51455, 51480, 51727, 51747, 51793, 51795, 52043, 52073, 52154, 52205, 52326, 52385, 52422, 52617, 52715, 52742, 52866, 53035, 53142, 53147, 53207, 53293, 53354, 53382, 53452, 53652, 53709, 54284, 54452, 54467, 54604, 54644, 54667, 54815, 54849, 54903, 54940, 54975, 54994, 55055, 55091, 55220, 55250, 55269, 55345, 55622, 55701, 55724, 55735, 55779, 55830, 55835, 56007, 56039, 56042, 56120, 56124, 56472, 56474, 56502, 56619, 56729, 56940, 56998, 57006, 57019, 57045, 57059, 57117, 57226, 57315, 57323, 57379, 57436, 57602, 57981, 58003, 58042, 58091, 58114, 58173, 58318, 58328, 58433, 58504, 58508, 58510, 58518, 58755, 58776, 58798, 58873, 58961, 59097, 59277, 59509, 59820, 60072, 60314, 60326, 60371, 60496, 60589, 60669, 60694, 60747, 60755, 60845, 60850, 60860, 60899, 60978, 61176, 61275, 61332, 61360, 61490, 61495, 61536, 61570, 61652, 61669, 61702, 61717, 61844, 61868, 61994, 62005, 62075, 62184, 62198, 62325, 62502, 62523, 62652, 62726, 62846, 62926, 62971, 63044, 63137, 63251, 63404, 63421, 63483, 63487, 63678, 63884, 64061, 64165, 64850, 65098, 65456, 65531, 65576, 65613, 65754, 65862, 65930, 65976, 65994, 66041, 66109, 66123, 66214, 66683, 66760, 67053, 67085, 67125, 67251, 67433, 67537, 67553, 67935, 67976, 68057, 68122, 68175, 68224, 68323, 68379, 68485, 68587, 68640, 68843, 69059, 69137, 69240, 69493, 69504, 69781, 69888, 69965, 70114, 70546, 70568, 70750, 70863, 71153, 71373, 71677, 71688, 72018, 72142, 72152, 72413, 72641, 72676, 72682, 72700, 72845, 72895, 72982, 73003, 73038, 73046, 73067, 73083, 73087, 73525, 73570, 73803, 73984, 74017, 74090, 74188, 74904, 74940, 75013, 75475, 75569, 75594, 76252, 76274, 76322, 76332, 76368, 76786, 76798, 76816, 77028, 77302, 77365, 77571, 77625, 77716, 77788, 77832, 77885, 78014, 78042, 78047, 78050, 78087, 78106, 78335, 78341, 78410, 78564, 78614, 78681, 78701, 78722, 78731, 78755, 78815, 78895, 78931, 79145, 79150, 79328, 79341, 79427, 79615, 79783, 79862, 79916, 80053, 80385, 80611, 81117, 81266, 81542, 81588, 82461, 82852, 83041, 83052, 83107, 83142, 83238, 83441, 83516, 83590, 83853, 84056, 84182, 84313, 85557, 85623, 85641, 85750, 85889, 86083, 86390, 86470, 86577, 86950, 86952, 87068, 87160, 87186, 87242, 87452, 87458, 87839, 87859, 88235, 88494, 88548, 88570, 88650, 88837, 88875, 88883, 88897, 88935, 88944, 89000, 89003, 89012, 89029, 89044, 89045, 89053, 89109, 89116, 89132, 89180, 89346, 89418, 89435, 89448, 89476, 89497, 89773, 89777, 89792, 89794, 89903, 90322, 90555, 90576, 90612, 90629, 90695, 90798, 91376, 91437, 91441, 91660, 91679, 91961, 92239, 92499, 92517, 92529, 93182, 93340, 93813, 93886, 94169, 94209, 94391, 94498, 94938, 94964, 95023, 95065, 95084, 95121, 95321, 95325, 95330, 95490, 95499, 95719, 95841, 95969, 95986, 96150, 96749, 98016, 98208, 98590, 98728, 98965, 99587, 99994, 100272, 100981, 101007, 103229, 103879, 104037, 104250, 104393, 104884, 105165, 105201, 105469, 105755, 105951, 105960, 106101, 106141, 106855, 106943, 106998, 107072, 107372, 108384, 108414, 108415, 108697, 108827, 108985, 109077, 109393, 109485, 109932, 110062, 110465, 110616, 110712, 110845, 111107, 111910, 112340, 112932, 113508, 113746, 114407, 114439, 115236, 115375, 115584, 115646, 115693, 116035, 116304, 116930, 118192, 118887, 119632, 120366, 120588, 120928, 120939, 121521, 121631, 123471, 124397, 124485, 125290, 125346, 125403, 125464, 125489, 125523, 125553, 125679, 125876, 125931, 126549, 127601, 127819, 128075, 128899, 129606, 130295, 130469, 130765, 130943, 131096, 131402, 132062, 132588, 133096, 133233, 133554, 134064, 134224, 134763, 135190, 135246, 135690, 135840, 136162, 136175, 136328, 136410, 136625, 136631, 140161, 142370, 144290, 146272, 146518, 147241, 147784, 148232, 148631, 149755, 150332, 150818, 151025, 152459, 153599, 154646, 155255, 155287, 155761, 158161, 158575, 158789, 159698, 160008, 160161, 161254, 161970, 162627, 163544, 163913, 164387, 164690, 165321, 165516, 165637, 166037, 166094, 166245, 167863, 168897, 169212, 170205, 170223, 170515, 170516, 170864, 171095, 171528, 171736, 171763, 172308, 172499, 172554, 172927, 173402, 173420, 173570, 173681, 173762, 174448, 174449, 174841, 175782, 176024, 176063, 176133, 176627, 176782, 177042, 177440, 177486, 179780, 180066, 180364, 180442, 181894, 184385, 185062, 185734, 187466, 187586, 188396, 188725, 189796, 189825, 189844, 189933, 190358, 190406, 190921, 195197, 195460, 196016, 196494, 197350, 197395, 198050, 199397, 201189, 201581, 203541, 203573, 203835, 203859, 203907, 204083, 204122, 204429, 204574, 204712, 205170, 206912, 208912, 208970, 209139, 209516, 209553, 210307, 212654, 212904, 212969, 213546, 214071, 216521, 216569, 216782, 216834, 217114, 220629, 221058, 221385, 223695, 224221, 224897, 225112, 228783, 228845, 228957, 229373, 229574, 232816, 232929, 233200, 233583, 233681, 233829, 234087, 238780, 239951, 241754, 244292, 246079, 247275, 249469, 250511, 250802, 250813, 250881, 251133, 253661, 254409, 254678, 258840, 264645, 264669, 268138, 268200, 272303, 273041, 273054, 273747, 277318, 281321, 281359, 281748, 281900, 282108, 285455, 286033, 286313, 286649, 286716, 286861, 287069, 287300, 287896, 288393, 288751, 291099, 291452, 291826, 291959, 292243, 292260, 292435, 293362, 296180, 296205, 296945, 297057, 297810}
)