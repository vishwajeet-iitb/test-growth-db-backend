#! /bin/bash
read -p "Enter the number of days for which db should be updated " d
today=`date -I`
for (( i=1 ; i<=$d ; i++ ));
do
	day=$(date +%Y%m%d  -d "$today - $i day")
	python manage.py importdata --migrate $day /mnt/growth_new/growth_data/ 
done


