#!/bin/bash

# A bash script to update a Cloudflare DNS A record with the external IP of the source machine
# Used to provide DDNS service for my home
# Needs the DNS record pre-creating on Cloudflare

# Proxy - uncomment and provide details if using a proxy
#export https_proxy=http://<proxyuser>:<proxypassword>@<proxyip>:<proxyport>

# Cloudflare zone is the zone which holds the record
zone=mcbcmusic.org
# dnsrecords is the A record which will be updated
dnsrecords=(app.mcbcmusic.org api.mcbcmusic.org appsh.mcbcmusic.org)

## Cloudflare authentication details
## Set these variables outside the script
#cloudflare_auth_email=email-addr
#cloudflare_auth_key=Global API token


# Get the current external IP address
ip=$(curl -s -X GET https://checkip.amazonaws.com)

echo "Current IP is $ip"

# get the zone id for the requested zone
zoneid=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$zone&status=active" \
  -H "X-Auth-Email: $cloudflare_auth_email" \
  -H "X-Auth-Key: $cloudflare_auth_key" \
  -H "Content-Type: application/json" | jq -r '{"result"}[] | .[0] | .id')

echo "Zoneid for $zone is $zoneid"

# loop dnsrecords
for dnsrecord in ${dnsrecords[@]}
do

  # check is host need to update
  if host $dnsrecord 1.1.1.1 | grep "has address" | grep "$ip"; then
    echo "$dnsrecord is currently set to $ip; no changes needed"
    continue
  fi

  # if here, the dns record needs updating

  # get the dns record id
  dnsrecordid=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records?type=A&name=$dnsrecord" \
    -H "X-Auth-Email: $cloudflare_auth_email" \
    -H "X-Auth-Key: $cloudflare_auth_key" \
    -H "Content-Type: application/json" | jq -r '{"result"}[] | .[0] | .id')

  echo "DNSrecordid for $dnsrecord is $dnsrecordid"

  if [ "$dnsrecord" = "appsh.mcbcmusic.org" ]; then
    proxied=false
  else
    proxied=true
  fi

  if [ "$dnsrecordid" = "null" ]; then
    # create the record
    echo "Creating DNS record for $dnsrecord"
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records" \
      -H "X-Auth-Email: $cloudflare_auth_email" \
      -H "X-Auth-Key: $cloudflare_auth_key" \
      -H "Content-Type: application/json" \
      --data "{\"type\":\"A\",\"name\":\"$dnsrecord\",\"content\":\"$ip\",\"ttl\":1,\"proxied\":$proxied}" 
  else
    # update the record
    echo "Updating DNS record for $dnsrecord"
    curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records/$dnsrecordid" \
      -H "X-Auth-Email: $cloudflare_auth_email" \
      -H "X-Auth-Key: $cloudflare_auth_key" \
      -H "Content-Type: application/json" \
      --data "{\"type\":\"A\",\"name\":\"$dnsrecord\",\"content\":\"$ip\",\"ttl\":1,\"proxied\":$proxied}" 

  fi

done