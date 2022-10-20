#!/bin/bash

export JAVA_HOME=/usr

sudo apt-get update
sudo apt-get -y install wget

HADOOP_VERSION=3.3.3
if [ ! -d ~/hadoop-$HADOOP_VERSION ];
then
	# install hadoop
	cd ~/
	wget https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
	tar -xzvf hadoop-$HADOOP_VERSION.tar.gz
fi

cd hadoop-$HADOOP_VERSION

cp $FFURF_HOME/deploy/hdfs/config/core-site.xml etc/hadoop/
cp $FFURF_HOME/deploy/hdfs/config/hdfs-site.xml etc/hadoop/
cp $FFURF_HOME/deploy/hdfs/config/hadoop-env.sh etc/hadoop/


which java
if [ $? != 0 ];
then
	sudo apt-get -y install default-jre
fi

bin/hdfs namenode -format
sbin/start-all.sh

echo "Started HDFS in standalone mode"
