{% set u_to = a.u_to.name %}
{% set user_bot = ctb.conf.reddit.auth.user %}

Hey!  You just got gold via dogetipbot!

{{ u_to | replace('_', '\_') }}, we've never met. If you'd like to use dogetipbot's to tip dogecoins to others, or buy
reddit gold for others with dogecoin please __[+register](http://www.reddit.com/message/compose?to={{ user_bot }}&subject=register&message=%2Bregister)__ first!

{% include 'footer.tpl' %}
