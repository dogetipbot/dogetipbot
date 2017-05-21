{% set user_from = a.u_from.name %}
Sorry {{ user_from | replace('_', '\_') }}, you don't have any coin balances enough for a tip.

{% include 'footer.tpl' %}
