# argument
# fast | compact

echo "[unit: sec]"
for dir in db_$1/*_log/
do
  echo "================================================"
  echo $dir

  printf "[HEADER] "
  for txt in $dir/*.txt
  do
    header_start=`grep -P -o '\[.*\](?= Imported new block headers)' $txt | head -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    header_end=`grep -P -o '\[.*\](?= Imported new block headers)' $txt | tail -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    header_start_sec=`date +%s -d ${header_start}`
    header_end_sec=`date +%s -d ${header_end}`
    header_diff=`expr ${header_end_sec} - ${header_start_sec}`
    printf ${header_diff}
    printf " "
  done

  printf "\n"
  printf "[RECEIPT] "
  for txt in $dir/*.txt
  do
    receipt_start=`grep -P -o '\[.*\](?= Imported new block receipts)' $txt | head -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    receipt_end=`grep -P -o '\[.*\](?= Imported new block receipts)' $txt | tail -n 2 | head -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    receipt_start_sec=`date +%s -d ${receipt_start}`
    receipt_end_sec=`date +%s -d ${receipt_end}`
    receipt_diff=`expr ${receipt_end_sec} - ${receipt_start_sec}`
    printf ${receipt_diff}
    printf " "
  done

  printf "\n"
  printf "[STATE] "
  for txt in $dir/*.txt
  do
    linenum=`grep -nr -P -o '\[.*\](?= Imported new block receipts)' $txt | tail -n 2 | head -n 1 | cut -d ":" -f 1`
    linenum=$(($linenum+1))
    state_start=`head -$linenum $txt | tail -n 1 | grep -P -o '\[.*\](?= Imported new state)' | grep -P -o "(?<=\|).*?(?=\])"`
    state_end=`grep -P -o '\[.*\](?= Imported new state)' $txt | tail -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    state_start_sec=`date +%s -d ${state_start}`
    state_end_sec=`date +%s -d ${state_end}`
    state_diff=`expr ${state_end_sec} - ${state_start_sec}`
    printf ${state_diff}
    printf " "
  done

  printf "\n"
  printf "[REPLAY] "
  for txt in $dir/*.txt
  do
    replay_start=`grep -P -o '\[.*\](?= Committed new head block)' $txt | grep -P -o "(?<=\|).*?(?=\])"`
    replay_end=`grep -P -o '\[.*\](?= Deallocated fast sync bloom)' $txt | grep -P -o "(?<=\|).*?(?=\])"`
    replay_start_sec=`date +%s -d ${replay_start}`
    replay_end_sec=`date +%s -d ${replay_end}`
    replay_diff=`expr ${replay_end_sec} - ${replay_start_sec}`
    printf ${replay_diff}
    printf " "
  done

  printf "\n"
  printf "[TOTAL] "
  for txt in $dir/*.txt
  do
    total_start=`grep -P -o '\[.*\](?= Block synchronisation started)' $txt | grep -P -o "(?<=\|).*?(?=\])"`
    total_end=`grep -P -o '\[.*\](?= Deallocated fast sync bloom)' $txt | grep -P -o "(?<=\|).*?(?=\])"`
    total_start_sec=`date +%s -d ${total_start}`
    total_end_sec=`date +%s -d ${total_end}`
    total_diff=`expr ${total_end_sec} - ${total_start_sec}`
    printf ${total_diff}
    printf " "
  done

  printf "\n"
  printf "[Restoration success - Deallocated fast sync bloom] "
  for txt in $dir/*.txt
  do
    diff_start=`grep -P -o '\[.*\](?= Deallocated fast sync bloom)' $txt | grep -P -o "(?<=\|).*?(?=\])"`
    diff_end=`grep -P -o '\[.*\](?= ### Restoration success)' $txt | tail -n 1 | grep -P -o "(?<=\|).*?(?=\])"`
    diff_start_sec=`date +%s -d ${diff_start}`
    diff_end_sec=`date +%s -d ${diff_end}`
    diff_diff=`expr ${diff_end_sec} - ${diff_start_sec}`
    printf ${diff_diff}
    printf " "
  done

  printf "\n"
done
echo "================================================"
