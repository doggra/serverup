#!/bin/bash

USER="__VAR_USER"
SERVERUUID ="__VAR_SERVER_UUID"
SSHKEY="__VAR_SSH_KEY"

echo ""
echo -e "\e[1;32mInstallation started..."

# Root required
if [ "$(id -u)" != "0" ]; then
    echo -e "\e[1;31mThis script must be run as root." 1>&2
    echo -e "\e[0m"
    exit 1
fi
echo -e "\e[0;32mRoot access granted."
echo -e "\e[0m"

# Check for system type
if [[ $(awk -F '=' '/DISTRIB_ID/ { print $2 }' /etc/*-release) == "Ubuntu" ]]; then
    BACKEND="sudo apt-get"
    SYSTEM="2"
    echo "System detected: Ubuntu"
elif [ -f /etc/debian_version ]; then
    BACKEND="apt-get"
    SYSTEM="0"
    echo "System detected: Debian"
elif [ -f /etc/redhat-release ]; then
    BACKEND="yum"
    SYSTEM="1"
    echo "System detected: Redhat/CentOS"
else
    echo -e "\e[1;31mNo supported system detected." 1>&2
    echo -e "\e[0m"
    exit 1
fi

# Get hostname
HOSTNAME=$(hostname -f)
if ! [ -z "$HOSTNAME" ]; then
    echo "Hostname: ${HOSTNAME}"
else
    echo -e "\e[1;31mNo hostname detected." 1>&2
    echo -e "\e[0m"
    exit 1
fi


# Get environment variables
xargs -n 1 -0 < /proc/${$}/environ | sed -n 's/^ENV_VAR_NAME=\(.*\)/\1/p'


# Get SSH Port
SSHPORT=${SSH_CONNECTION##* }
if ! [ "$SSHPORT" -eq "$SSHPORT" ] 2>/dev/null; then
    echo -e "\e[1;31mSSH port not found." 1>&2
    echo -e "\e[0m"
    exit 1
fi
echo "SSH port: ${SSHPORT}"

echo ""
echo "Installing ..."

# Get SSH IP
SSHIP=$(echo ${SSH_CONNECTION} | awk '{print $3}')

# Check for dependencies
if ! hash wget 2>/dev/null; then
    echo "Dependency wget will be installed"
    ${BACKEND} -y install wget &> /dev/null
fi

# Uninstall old SSH keys
sed -i '/up2secure/d' ~/.ssh/authorized_keys &> /dev/null
sed -i '/up2secure/d'/etc/ssh/sshd_config &> /dev/null

# Uninstall old instances (TODO)
# rm /usr/local/bin/updaix-rsh &> /dev/null
# rm /usr/local/bin/updaix-remove &> /dev/null

# Install the SSH key
if ! [ -d "~/.ssh" ]; then
    mkdir -p ~/.ssh
    if [ $? -ne 0 ] ; then
        echo -e "\e[1;31mSSH user directory could not be created.\e[0m" 1>&2
        echo ""
        exit 1
    fi
fi

if ! [ -a "~/.ssh/authorized_keys" ]; then
    touch ~/.ssh/authorized_keys
    if [ $? -ne 0 ] ; then
        echo -e "\e[1;31mSSH authorized_keys file could not be created.\e[0m" 1>&2
        echo ""
        exit 1
    fi
fi

# Add SSH key to authorized keys.
echo "${SSHKEY}" >> ~/.ssh/authorized_keys

# Set privileges
chmod 700 ~/.ssh && chmod 600 ~/.ssh/*

# Enable public key authorization
if ! [ -a "/etc/ssh/sshd_config" ]; then
    echo -e "\e[31mSSHD config file not found."
    echo -e "\e[31mPlease ensure that public key authorization is allowed."
else
    echo "" >> /etc/ssh/sshd_config
    echo "# up2secure config" >> /etc/ssh/sshd_config
    echo "RSAAuthentication yes # up2secure" >> /etc/ssh/sshd_config
    echo "PubkeyAuthentication yes # up2secure" >> /etc/ssh/sshd_config
    echo "PermitRootLogin yes # up2secure" >> /etc/ssh/sshd_config
fi

# Callback to Django ap[]
echo "Checking access to server..."
OUTPUT=$(wget -q  --post-data="s=${SERVERUUID}&u=${USER}&i=${SSHIP}&h=${HOSTNAME}&d=${SYSTEM}&p=${SSHPORT}" -O - "__VAR_HOSTNAME_FOR_URL")
if ! [ "$OUTPUT" == "OK" ]; then
    echo -e "\e[1;31mNo access to this server." 1>&2
    echo -e "\e[1;31mPlease try it again." 1>&2
    echo -e "\e[0m${OUTPUT}"
    echo -e "\e[0m"
    exit 1
else
    echo -e "\e[0;32mAccess to server works!"
    echo -e "\e[0m"
fi

echo -e "\e[1;32mInstallation finished\e[0m"
echo ""

