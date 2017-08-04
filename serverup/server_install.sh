#!/bin/bash

USER="__VAR_USER"
SERVERUUID="__VAR_SERVER_UUID"
HOSTNAME=$(hostname -f)
SSHPORT=${SSH_CONNECTION##* }
SSHIP=$(echo ${SSH_CONNECTION} | awk '{print $3}')
SSHKEY="__VAR_SSH_KEY"

if [ "$(id -u)" != "0" ]; then
    echo -e "This script must be run as root." 1>&2
    exit 1
fi

if [ -f /etc/debian_version ]; then
    BACKEND="apt-get"
    SYSTEM="0"
elif [ -f /etc/redhat-release ]; then
    BACKEND="yum"
    SYSTEM="1"
fi

if ! [ "$SSHPORT" -eq "$SSHPORT" ] 2>/dev/null; then
    echo -e "SSH port not found!" 1>&2
    exit 1
fi

# Install wget if not exists
if ! hash wget 2>/dev/null; then ${BACKEND} -y install wget &>/dev/null; fi

echo "Uninstalling old instances if exists..."
rm /usr/local/bin/serverup-rsh &> /dev/null
sed -i '/serverup/d' ~/.ssh/authorized_keys &> /dev/null
sed -i '/serverup/d' /etc/ssh/sshd_config &> /dev/null
rm /usr/local/bin/serverup-uninstall &> /dev/null

echo "Installing restricted shell..."
cat <<\EOT >> /usr/local/bin/serverup-rsh
#!/bin/bash

if [[ -z $SSH_ORIGINAL_COMMAND ]]
then
    echo "Pong"
    exit 1
fi

case $SSH_ORIGINAL_COMMAND in
    "id" | \
    "apt-get update -qq && apt-get upgrade -s" | "sudo apt-get update -qq && apt-get upgrade -s" | \
    "apt-get autoclean -y" | "sudo apt-get autoclean -y" | \
    "dpkg --configure -a" | "yum check-update -q" | \
    "/usr/local/bin/serverup-uninstall")
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    "yum update "*)
        SUBSTRING=$(echo $SSH_ORIGINAL_COMMAND | cut -c -12)
        if [[ "$SUBSTRING" =~ [^a-zA-Z0-9\-\ ] ]]; then
            echo "Command not allowed: $SSH_ORIGINAL_COMMAND"
            exit 2
        fi
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    "apt-get install --only-upgrade "*)
        SUBSTRING=$(echo $SSH_ORIGINAL_COMMAND | cut -c -32)
        if [[ "$SUBSTRING" =~ [^a-zA-Z0-9\-\ ] ]]; then
            echo "Command not allowed: $SSH_ORIGINAL_COMMAND"
            exit 2
        fi
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    *)
        echo "Command not allowed: $SSH_ORIGINAL_COMMAND"
        exit 2
        ;;
esac
EOT
chmod +x /usr/local/bin/serverup-rsh

echo "Copying uninstallation script..."
cat <<\EOT >> /usr/local/bin/serverup-uninstall
#!/bin/bash
# Deinstallation script
if["$(id -u)"!="0"];then echo "This script must be run as root";fi
rm /usr/local/bin/serverup-rsh &> /dev/null
sed -i '/serverup/d'/etc/ssh/sshd_config &> /dev/null
sed -i '/serverup/d' ~/.ssh/authorized_keys &> /dev/null
rm /usr/local/bin/serverup-uninstall &> /dev/null
exit 1
EOT
chmod +x /usr/local/bin/serverup-uninstall

echo "Installing SSH access..."
if ! [ -d "~/.ssh" ]; then
    mkdir -p ~/.ssh
    if [ $? -ne 0 ] ; then
        echo -e "Can't create SSH directory." 1>&2
        echo ""
        exit 1
    fi
fi
if ! [ -a "~/.ssh/authorized_keys" ]; then
    touch ~/.ssh/authorized_keys
    if [ $? -ne 0 ] ; then
        echo -e "Couldn't create SSH authorized_keys file could not be created." 1>&2
        echo ""
        exit 1
    fi
fi

echo "command=\"/usr/local/bin/serverup-rsh\" ${SSHKEY}" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/*
if ! [ -a "/etc/ssh/sshd_config" ]; then
    echo -e "\e[31m/etc/ssh/sshd_config not found."
    echo -e "\e[31mpublic key authorization not allowed?"
else
    echo "" >> /etc/ssh/sshd_config
    echo "# serverup config" >> /etc/ssh/sshd_config
    echo "RSAAuthentication yes # serverup" >> /etc/ssh/sshd_config
    echo "PubkeyAuthentication yes # serverup" >> /etc/ssh/sshd_config
    echo "PermitRootLogin yes # serverup" >> /etc/ssh/sshd_config
fi

echo "Checking connection to control app..."
OUTPUT=$(wget -q  --post-data="s=${SERVERUUID}&u=${USER}&i=${SSHIP}&h=${HOSTNAME}&d=${SYSTEM}&p=${SSHPORT}" -O - "__VAR_HOSTNAME_FOR_URL")
if ! [ "$OUTPUT" == "OK" ]; then
    echo -e "${OUTPUT}"
    exit 1
fi

echo -e "Installation finished!"

