{% set user_from = a.u_from.name %}
{% set user_to = a.u_to.name %}
{% set balance_fmt = "%.8f dogecoins" % (balance) %}
{% set coin_amount = a.coin_val %}
{% set coinval_fmt = "%s%s%.6g %s%s" % (amount_prefix_short, ctb.conf.coins[a.coin].symbol, coin_amount, amount_prefix_long, ctb.conf.coins[a.coin].name) %}
{% set fiatval_fmt = "%s%.3f" % (ctb.conf.fiat[a.fiat].symbol, a.fiat_val) %}
Hey {{ user_to | replace('_', '\_') }}, you have received a __{{ coinval_fmt }} ({{ fiatval_fmt }})__ tip from /u/{{ user_from }}.

such current balance: {{ balance_fmt }}

need to deposit more? your deposit account is: {{ addr }}

{% set user = user_to %}
{% include 'footer.tpl' %}
