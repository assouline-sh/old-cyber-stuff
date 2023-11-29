#!/bin/bash
# Check if password has been pwnd using the site Have I Been Pwnd?
# But instead of sending our plaintext password, send part of its hash,
# enough to determine if the site has the password in its database

given_pass=$1
hash_pass=$(echo -n $given_pass | sha1sum | awk '{print substr($1, 0, 32)}')

prefix=$(echo $hash_pass | awk '{print substr($1, 0, 5)}')
suffix=$(echo $hash_pass | awk '{print substr($1, 6, 26)}')
if curl -s https://api.pwnedpasswords.com/range/$prefix | grep -i $suffix > /dev/null; then
    	echo "Password has been pwned. Change it!";
else
    	echo "Password is safe to use :)";
fi

