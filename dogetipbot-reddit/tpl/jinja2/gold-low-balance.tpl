{% set user_from = a.u_from.name %}
I'm sorry {{ user_from | replace('_', '\_') }}, your balance is insufficient to buy reddit gold. Please deposit more coins
and try again.

{% include 'footer.tpl' %}
