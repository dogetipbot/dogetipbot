{% set user_from = a.u_from.name %}
{% set amt = "%.8f DOGE" % (a.coin_val) %}


Hmm... So, {{user_from}}...

Well, this is awkward.

Right now dogetipbot doesn't have enough in our hot wallet to cover your {{amt}} withdrawal. We'll need to withdraw funds from cold storage to cover this.

Thanks for your patience.

{% include 'footer.tpl' %}
