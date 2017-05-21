{% set user = a.u_from.name.lower() %}
{% set balance_fmt = "%.8f DOGE" % (balance) %}
{% set sent_fmt = "%.8f DOGE" % (sent) %}
{% set rcvd_fmt = "%.8f DOGE" % (rcvd) %}
{% if usd_sent: %}
{% set sent_usd_fmt = "%.2f" % (usd_sent) %}
{% else %}
{% set send_usd_fmt = "0.0" %}
{% endif %}
{% if usd_rcvd: %}
{% set rcvd_usd_fmt = "%.2f" % (usd_rcvd) %}
{% else %}
{% set rcvd_usd_fmt = "0.0" %}
{% endif %}

Hello {{ user | replace('_', '\_') }}, here are your last {{ limit }} transactions.

* Your current balance is: **{{ balance_fmt }}**
* Your deposit address is: {{ addr }}
* **You've tipped:** {{ sent_fmt }} **(${{sent_usd_fmt}})**
* **You've been tipped:** {{ rcvd_fmt }} **(${{rcvd_usd_fmt}})**

{{ "|".join(keys) }}
{{ "|".join([":---"] * (keys|length)) }}
{% for h in history %}
{{   "|".join(h) }}
{% endfor %}

{% include 'footer.tpl' %}
