#!/bin/bash

SERVICE_NAME=superbot
BOT_PATH="/root/z/superbot.py"
PYTHON_BIN=$(which python3)

# Check Python exists
if [ -z "$PYTHON_BIN" ]; then
  echo "[ERROR] Python3 not found!"
  exit 1
fi

# Ensure directory exists
mkdir -p /root/z

# Create systemd service
cat <<EOF > /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=Ultimate Telegram Terminal Bot
After=network.target

[Service]
ExecStart=${PYTHON_BIN} ${BOT_PATH}
WorkingDirectory=/root/z
Restart=always
RestartSec=5
User=root
StandardOutput=append:/root/z/superbot_stdout.log
StandardError=append:/root/z/superbot_stderr.log

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chmod 644 /etc/systemd/system/${SERVICE_NAME}.service

# Reload, enable, and start the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

echo "Superbot service installed and running at boot."
systemctl status ${SERVICE_NAME} --no-pager