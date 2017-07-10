#!/bin/bash
for NUM in $(seq $1)
do
	let PORT=$((140+$NUM))
	cp -r sitl_gazebo/models/f450-1 sitl_gazebo/models/f450-tmp-$NUM
	mv sitl_gazebo/models/f450-tmp-$NUM/f450-1.sdf sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf
	sed -i "s/146/$PORT/g" sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf 
	cp ../posix-configs/SITL/init/lpe/f450-1 ../posix-configs/SITL/init/lpe/f450-tmp-$NUM
	sed -i "s/146/$PORT/g" ../posix-configs/SITL/init/lpe/f450-tmp-$NUM
done
touch  ../launch/posix_sitl_multi_tmp.launch

#Build launchfile from ground up
SOURCE="../launch/posix_sitl_multibase.launch"
DEST="../launch/posix_sitl_multi_tmp.launch"
sed -n 1,10p $SOURCE>>$DEST
OLD=1

#xy positions
for NUM in $(seq $1)
do
	sed -i "11s/x$OLD/x$NUM/g" $SOURCE
	sed -i "12s/y$OLD/y$NUM/g" $SOURCE
	sed -i "12s/$OLD/$NUM/g" $SOURCE
	sed -n 11,12p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "11s/x$NUM/x1/g" $SOURCE
sed -i "12s/y$NUM/y1/g" $SOURCE
sed -i "12s/$NUM/1/g" $SOURCE

sed -n 13,15p $SOURCE>>$DEST

OLD=1
#vehicle
for NUM in $(seq $1)
do
	sed -i "16s/$OLD/$NUM/g" $SOURCE
	sed -n 16p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "16s/$NUM/1/g" $SOURCE
sed -n 17p $SOURCE>>$DEST
OLD=1
#rcs/sdf
for NUM in $(seq $1)
do
	sed -i "18,19s/$OLD/$NUM/g" $SOURCE
	sed -n 18,19p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "18,19s/$NUM/1/g" $SOURCE
sed -n 20,33p $SOURCE>>$DEST
OLD=1
#sitl
for NUM in $(seq $1)
do
	sed -i "34,36s/$OLD/$NUM/g" $SOURCE
	sed -n 34,36p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "34,36s/$NUM/1/g" $SOURCE
sed -n 37,47p $SOURCE>>$DEST
OLD=1
#spawn node
for NUM in $(seq $1)
do
	sed -i "48,50s/$OLD/$NUM/g" $SOURCE
	sed -n 48,50p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "48,50  s/$NUM/1/g" $SOURCE
sed -n 51p $SOURCE>>$DEST

OLD=1
#mavros node
for NUM in $(seq $1)
do
	sed -i "52s/$OLD/$NUM/g" $SOURCE
	sed -n 52p $SOURCE>>$DEST
	sed -i "53s/14$OLD/14$NUM/g" $SOURCE
	sed -n 53p $SOURCE>>$DEST
	sed -n 54p $SOURCE>>$DEST
	sed -i "55,57s/$OLD/$NUM/g" $SOURCE
	sed -n 55,57p $SOURCE>>$DEST
	sed -n 58,60p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "52s/$NUM/1/g" $SOURCE
sed -i "53s/14$NUM/141/g" $SOURCE
sed -i "55,57s/$NUM/1/g" $SOURCE
sed -n 61,64p $SOURCE>>$DEST

sed -i 's/px1/px4/g' $SOURCE
sed -i 's/f150/f450/g' $SOURCE






echo "$1 DRONES CREATED!"

