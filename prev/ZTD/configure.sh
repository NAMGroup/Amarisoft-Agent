#!/bin/bash

#https://unix.stackexchange.com/questions/31414/how-can-i-pass-a-command-line-argument-into-a-shell-script

helpFunction()
{
   echo ""
   echo "Usage: $0 -n agent_name  -s server_ip -p agent_port -i agent_ip"
   echo -e "\t-n The name of the agent"
   echo -e "\t-s The IP:port of the server"
   echo -e "\t-p The port to be used"
   echo -e "\t-i The ip of the gnb  to be used"
   exit 1 # Exit script after printing help
}

while getopts "n:s:p:i:" opt
do
   case "$opt" in
      n ) agent_name="$OPTARG" ;;
      s ) server_ip="$OPTARG" ;;
      p ) agent_port="$OPTARG" ;;
      i ) agent_ip="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$agent_name" ] || [ -z "$server_ip" ] || [ -z "$agent_port" ] || [ -z "$agent_ip" ]
then

   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$agent_name"
echo "$server_ip"
echo "$agent_port"
echo "$agent_ip"
# Change server
sed -i "s/SERVER_PLACEHOLDER/$server_ip/" ../agent/src/conf_data_RW.yml

# Change name
sed -i "s/NAME_PLACEHOLDER/$agent_name/" ../agent/src/resource_data_RO.yml


# Change ip/port
sed -i "s/PORT_PLACEHOLDER/$agent_port/" ../agent/src/resource_data_RO.yml
sed -i "s/IP_PLACEHOLDER/$agent_ip/" ../agent/src/resource_data_RO.yml

# Change port in dockerfile
sed -i "s/PORT_PLACEHOLDER/$agent_port/" ../agent/docker-compose.yml

