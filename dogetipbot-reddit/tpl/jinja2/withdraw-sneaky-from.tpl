{% set user_from = a.u_from.name %}
{% set balance_fmt = "%.6g dogecoins" % (balance) %}
{% set user_to = a.u_to.name %}
{% set coin_amount = a.coin_val %}
{% set coinval_fmt = "%s%.6g %s" % (ctb.conf.coins[a.coin].symbol, a.coin_val, ctb.conf.coins[a.coin].name) %}
{% set fiatval_fmt = "%s%.6g" % (ctb.conf.fiat[a.fiat].symbol, a.fiat_val) %}
Hey {{ user_from | replace('_', '\_') }}, you sent __{{ coinval_fmt }} dogecoins to /u/{{ user_to }}.

such wow -- you tried to send to an address, but it happens to be owned by /u/{{ user_to }}

we went ahead and sent those coins over direct. you know, cause that's kinda what we do.

if that's your alt account... we'll keep your secret safe.

much shhhs

many secrets

wow

such current balance: {{ balance_fmt }}

balance getting low? here's your deposit address: {{ addr }}

wow

much tip

such generosity

{% set user = user_from %}
{% include 'footer.tpl' %}
