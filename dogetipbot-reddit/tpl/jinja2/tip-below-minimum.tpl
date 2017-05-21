{% set user_from = a.u_from.name %}
{% set amount_fmt = "%.8g %s" % (a.coin_val, a.coin.upper()) %}
{% set min_fmt = "%.10g" % min_value %}
{% set coin_name = ctb.conf.coins[a.coin].name %}
I'm sorry {{ user_from | replace('_', '\_') }}, your tip/withdraw of __{{ amount_fmt }}__ is below the minimum of __{{ min_fmt }}__.

If you really need to withdraw this amount, try depositing some more dogecoins to meet the minimum limit, then withdrawing everything.

{% include 'footer.tpl' %}
