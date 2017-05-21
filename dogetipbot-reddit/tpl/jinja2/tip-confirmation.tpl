{% set title_fmt = "__^[%s]__:" % title %}
{% if a.type == 'givetip' and a.keyword and ctb.conf.keywords[a.keyword].title: %}
{%   set title_fmt = ctb.conf.keywords[a.keyword].title %}
{% endif %}
{% set user_from_fmt = " ^/u/%s" % a.u_from.name %}
{% set arrow_fmt = " ^->" %}
{% if a.u_to: %}
{%   set user_to_fmt = " ^/u/%s" % a.u_to.name %}
{%   if ctb.conf.reddit.stats.enabled: %}
{%     set stats_user_to_fmt = " ^^[[stats]](%s_%s)" % (ctb.conf.reddit.stats.url, a.u_to.name) %}
{%   endif %}
{% else %}
{%   set ex = ctb.conf.coins[a.coin].explorer %}
{%   set user_to_fmt = " ^[%s](%s%s)" % (a.addr_to, ex.address, a.addr_to) %}
{%   set arrow_fmt = " ^[->](%s)" % (ex.transaction) %}
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
{% if ctb.conf.reddit.stats.enabled: %}
{%   set stats_user_from_fmt = " ^^[[stats]](%s_%s)" % (ctb.conf.reddit.stats.url, a.u_from.name) %}
{%   set stats_link_fmt = " ^[[stats]](%s)" % ctb.conf.reddit.stats.url %}
{% endif %}
{% if ctb.conf.reddit.help.enabled: %}
{%   set help_link_fmt = " ^[[help]](%s)" % ctb.conf.reddit.help.url %}
{% endif %}
{{ title_fmt }}{{ user_from_fmt }}{{ stats_user_from_fmt }}{{ arrow_fmt }}{{ user_to_fmt }}{{ stats_user_to_fmt }}{{ coin_amount_fmt }}{{ fiat_amount_fmt }}{{ help_link_fmt }}{{ stats_link_fmt }}
