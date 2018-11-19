#/bin/bash

hadoop_command='hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.2.0.jar -files mapper.py,reducer.py -mapper mapper.py -reducer reducer.py'
mv='hadoop fs -mv '
rm='hadoop fs -rm -r'
cp2local='hadoop fs -copyToLocal '
input='tempinput'

for (( i = 1; i < $1+1; i++ )); do
    echo "Page Rank Iteration $i"
    output="pagerank_tempoutput_$i"
    eval "$hadoop_command -input $input -output $output -jobconf mapred.job.name=\"Page Rank Iteration $i\""
    input=$output
    eval "$rm $input/_SUCCESS"
done

mkdir ~/pagerank_result
eval "$cp2local $output/* ~/pagerank_result"

