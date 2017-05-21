#!/bin/bash
mysql -u root --password=xxx dogetipbot << EOF
insert into t_unprocessed_transactions (txid) values('${1}');
EOF