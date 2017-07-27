#!/bin/bash
USER="__VAR_USER"
SERVERUUID="__VAR_SERVER_UUID"
HOSTNAME=$(hostname -f)
SSHPORT=${SSH_CONNECTION##* }
SSHIP=$(echo ${SSH_CONNECTION} | awk '{print $3}')
SSHKEY="__VAR_SSH_KEY"

if [ "$(id -u)" != "0" ]; then
    echo -e "\e[1;31mThis script must be run as root." 1>&2
    echo -e "\e[0m"
    exit 1
fi
if [[ $(awk -F '=' '/DISTRIB_ID/ { print $2 }' /etc/*-release) == "Ubuntu" ]]; then
    BACKEND="sudo apt-get"
    SYSTEM="2"
elif [ -f /etc/debian_version ]; then
    BACKEND="apt-get"
    SYSTEM="0"
elif [ -f /etc/redhat-release ]; then
    BACKEND="yum"
    SYSTEM="1"
fi
xargs -n 1 -0 < /proc/${$}/environ | sed -n 's/^ENV_VAR_NAME=\(.*\)/\1/p'
if ! [ "$SSHPORT" -eq "$SSHPORT" ] 2>/dev/null; then
    echo -e "\e[1;31mSSH port not found." 1>&2
    echo -e "\e[0m"
    exit 1
fi

if ! hash wget 2>/dev/null; then
    ${BACKEND} -y install wget &> /dev/null
fi

# Uninstall old instances
rm /usr/local/bin/serverup-rsh &> /dev/null
sed -i '/serverup/d' ~/.ssh/authorized_keys &> /dev/null
sed -i '/serverup/d'/etc/ssh/sshd_config &> /dev/null
rm /usr/local/bin/serverup-remove &> /dev/null

# Copy the restricted shell
cat <<\EOT >> /usr/local/bin/serverup-rsh
#!/bin/bash
# Restricted shell of serverUP

if [[ -z $SSH_ORIGINAL_COMMAND ]]
then
    echo "updAIX restricted shell: interactive shell not allowed"
    exit 1
fi

case $SSH_ORIGINAL_COMMAND in
    "apt-get autoclean -y" | "sudo apt-get autoclean -y" | \
    "apt-get update -qq" | "sudo apt-get update -qq" | \
    "apt-get upgrade -s" | "sudo apt-get upgrade -s" | \
    "dpkg --configure -a" | "yum check-update -q" | "/usr/local/bin/serverup-remove")
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    "yum update "*)
        SUBSTRING=$(echo $SSH_ORIGINAL_COMMAND | cut -c -12)
        if [[ "$SUBSTRING" =~ [^a-zA-Z0-9\-\ ] ]]; then
            echo "updAIX restricted shell: command not allowed: $SSH_ORIGINAL_COMMAND"
            exit 2
        fi
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    "apt-get install --only-upgrade "*)
        SUBSTRING=$(echo $SSH_ORIGINAL_COMMAND | cut -c -32)
        if [[ "$SUBSTRING" =~ [^a-zA-Z0-9\-\ ] ]]; then
            echo "updAIX restricted shell: command not allowed: $SSH_ORIGINAL_COMMAND"
            exit 2
        fi
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    "sudo apt-get install --only-upgrade "*)
        SUBSTRING=$(echo $SSH_ORIGINAL_COMMAND | cut -c -37)
        if [[ "$SUBSTRING" =~ [^a-zA-Z0-9\-\ ] ]]; then
            echo "updAIX restricted shell: command not allowed: $SSH_ORIGINAL_COMMAND"
            exit 2
        fi
        bash -c "$SSH_ORIGINAL_COMMAND"
        ;;
    *)
        echo "updAIX restricted shell: command not allowed: $SSH_ORIGINAL_COMMAND"
        exit 2
        ;;
esac
EOT
chmod +x /usr/local/bin/serverup-rsh
echo "Restricted shell installed"

# Copy the uninstallation script
cat <<\EOT >> /usr/local/bin/serverup-remove
#!/bin/bash
# Deinstallation script

# Enforce root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

# Deinstall routine
rm /usr/local/bin/serverup-rsh &> /dev/null
sed -i '/serverup/d' ~/.ssh/authorized_keys &> /dev/null
sed -i '/serverup/d'/etc/ssh/sshd_config &> /dev/null
rm /usr/local/bin/serverup-remove &> /dev/null

exit 1
EOT
chmod +x /usr/local/bin/serverup-remove
echo "Deinstallation script copied"

# Install SSH
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
echo "${SSHKEY}" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/*
if ! [ -a "/etc/ssh/sshd_config" ]; then
    echo -e "\e[31mSSHD config file not found."
    echo -e "\e[31mPlease ensure that public key authorization is allowed."
else
    echo "" >> /etc/ssh/sshd_config
    echo "# serverup config" >> /etc/ssh/sshd_config
    echo "RSAAuthentication yes # serverup" >> /etc/ssh/sshd_config
    echo "PubkeyAuthentication yes # serverup" >> /etc/ssh/sshd_config
    echo "PermitRootLogin yes # serverup" >> /etc/ssh/sshd_config
fi

# Callback to Django
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

