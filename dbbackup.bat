cd D:\caika\mysql-8.0.31\bin
set filename=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%
mysqldump -uroot -pcaika2020  --databases caika > D:\caika\data\db.sql.%filename%