#!/bin/bash

PIA_PASSWORD=`cat password`
FILES=/etc/NetworkManager/system-connections/PIA*

for f in ${FILES}
do
	sudo sed -i "\$a[vpn-secrets]\npassword=${PIA_PASSWORD}" "$f"
	sudo sed -i "s/\(password-flags *= *\).*/\10/" "$f"
done
