#!/bin/bash

#Needs a file called 'password' with your password in the same folder
PIA_PASSWORD=`cat password`
FILES=/etc/NetworkManager/system-connections/PIA*

for f in ${FILES}
do
	sudo sed -i "\$a[vpn-secrets]\npassword=${PIA_PASSWORD}" "$f"
	sudo sed -i "s/\(password-flags *= *\).*/\10/" "$f"
done
