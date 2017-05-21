#!/bin/bash
/usr/bin/mysql -u username --password=password haikuberu << EOF
insert into unprocessed (txid) values('${1}');
EOF