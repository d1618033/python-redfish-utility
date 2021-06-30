
#!/bin/bash

ilorest rawget /redfish/v1/Systems/1/Storage/ | grep 'Storage\/DA' | cut -f4 -d'"' >  disk.list

rm -f ilorest_input.list

# create list of NVMe targets.
while
        read i
do
        echo -n $i >> ilorest_input.list
        echo -n "Drives/" >> ilorest_input.list
        echo $i | cut -f7 -d'/' >> ilorest_input.list
done < disk.list

# Turn on the Indicator LED for each NVMe target device.
while
        read i
do
        name=`echo $i | cut -f9 -d'/'`
        echo "name = $name"
        sed "s/XXX/$name/g" lit_template.json > lit.json
        ilorest rawpatch lit.json
done < ilorest_input.list

# Display Indicator LED setting.
while
        read i
do
        echo -e "\n=> $i"
        ilorest rawget $i | grep Indicator
done < ilorest_input.list

# Turn off the Indicator LED for each NVMe target device.
while
        read i
do
        name=`echo $i | cut -f9 -d'/'`
        echo "name = $name"
        sed "s/XXX/$name/g" off_template.json > off.json
        ilorest rawpatch off.json
done < ilorest_input.list

# Display Indicator LED setting.
while
        read i
do
        echo -e "\n=> $i"
        ilorest rawget $i | grep Indicator
done < ilorest_input.list

