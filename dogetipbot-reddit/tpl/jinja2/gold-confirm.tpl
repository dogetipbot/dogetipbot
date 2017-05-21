{% set title_fmt = "__^[%s]__:" % title %}
{% set user_from_fmt = " ^/u/%s" % a.u_from.name %}
{% set arrow_fmt = " ^->" %}
{% if a.u_to: %}
{%   set user_to_fmt = " ^/u/%s" % a.u_to.name %}
{% endif %}
{% if a.coin_val: %}
{%   set coin_amount = a.coin_val %}
{%   set coin_name = ctb.conf.coins[a.coin].name %}
{%   set coin_symbol = ctb.conf.coins[a.coin].symbol %}
{%   set coin_amount_fmt = (" __^%s" % coin_symbol) + ('%.8f' % coin_amount).rstrip('0').rstrip('.') + (" ^%ss__" % coin_name) %}
{% endif %}
{% if a.fiat_val: %}
{%   set fiat_amount = a.fiat_val %}
{%   set fiat_symbol = ctb.conf.fiat[a.fiat].symbol %}
{%   set fiat_amount_fmt = "&nbsp;^__(%s%.6g)__" % (fiat_symbol, fiat_amount) %}
{% endif %}
{% if ctb.conf.reddit.help.enabled: %}
{%   set help_link_fmt = " ^[[help]](%s)" % ctb.conf.reddit.help.url %}
{% endif %}
{{ title_fmt }}{{ user_from_fmt }}{{ arrow_fmt }}{{ user_to_fmt }}{{ coin_amount_fmt }}{{ fiat_amount_fmt }}{{ help_link_fmt }}
