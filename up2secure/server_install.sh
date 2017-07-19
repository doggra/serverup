#!/bin/bash

SSHKEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDM9h/sKQEUHjiAWJo7wMx8V9D1XXvDIrRgbie9oryDxVBPFAtWLRhzv1+NbaAexljTIXGbfB7oy2HUKzwmVmQ21Y0Wrl863Fdw3HZU8ZFhiQWSh6MNNfYWMZ668INeoIwohVdZYqIoU6d2Ldaj4jG/AoQ/KLH6556YVeSLRExioV3y9oHBBN1vTG/zr9VtWSwgxcNlfTFlij1HB9SJfcb+RE3GAbLg0xCccmqttmlRHbGspe96YaVXuknmLK49SOLiGm/Yu9ySAU+FMh3Lgv2/2o6CNFzQ0TJjD6TgLGhwt536lDNLwDMyWxCWrbW5cgDtwZgPn8wIsqbL3Sdh0Qmfp/3UKhPNFmfr7yUasEsPBRRWNQ7JeqRmnUVssOiJbBNBmzey+om5A88xCRWMzYzhh+AUFLr5OD8GDKysFdhThAICD3/9cvE5flLUbi0x2N1xPQ+RhHpeNHE6qJwoPKN38BcZxhDmU74v8yJ5bUbAwCauGebGaYGFFlUgWQ3ctnfr9xUH5W1+SsPZzABWU4UvHpTkpAcGQa0HJ4LxqiHyVu73sFrHzDXFP8u5iqMHWj/CB9pBk5zbnBi6opWLcBDq8UiqqnHnLDInd1wZaeP9mDcHgSEBdZWjjzhvflmrKINPjukiU28RQDg7FkaRwfncLtFvYwPuYz66Lxm0RWelbw== up2secure"

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
    SYSTEM="U"
    echo "System detected: Ubuntu"
elif [ -f /etc/debian_version ]; then
    BACKEND="apt-get"
    SYSTEM="D"
    echo "System detected: Debian"
elif [ -f /etc/redhat-release ]; then
    BACKEND="yum"
    SYSTEM="R"
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

# Get ssh port
SSHPORT=${SSH_CONNECTION##* }
if ! [ "$SSHPORT" -eq "$SSHPORT" ] 2>/dev/null; then
    echo -e "\e[1;31mSSH port not found." 1>&2
    echo -e "\e[0m"
    exit 1
fi
echo "SSH port: ${SSHPORT}"

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
    else
        echo "SSH user directory created."
    fi
else
    echo "SSH user directory found."
fi

if ! [ -a "~/.ssh/authorized_keys" ]; then
    touch ~/.ssh/authorized_keys
    if [ $? -ne 0 ] ; then
        echo -e "\e[1;31mSSH authorized_keys file could not be created.\e[0m" 1>&2
        echo ""
        exit 1
    else
        echo "SSH authorized_keys file created."
    fi
else
    echo "SSH authorized_keys file found."
fi

echo "${SSHKEY}" >> ~/.ssh/authorized_keys
echo "SSH key added (restricted access)."

chmod 700 ~/.ssh && chmod 600 ~/.ssh/*
echo "SSH user directory mode had set."

# Enable public key authorization
if ! [ -a "/etc/ssh/sshd_config" ]; then
    echo -e "\e[31mSSHD config file not found."
    echo -e "\e[31mPlease ensure that public key authorization is allowed."
else
    echo "SSHD config file found."
    echo "" >> /etc/ssh/sshd_config
    echo "# up2secure config" >> /etc/ssh/sshd_config
    echo "RSAAuthentication yes # up2secure" >> /etc/ssh/sshd_config
    echo "PubkeyAuthentication yes # up2secure" >> /etc/ssh/sshd_config
    echo "PermitRootLogin yes # up2secure" >> /etc/ssh/sshd_config
    echo "Public key authorization enabled"
fi