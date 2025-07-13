FROM amazonlinux:2023

# Install Python 3.11 and build tools
RUN dnf install -y python3.11 python3.11-pip gcc rust cargo zip

# Symlink python3.11 as default python/pip
RUN alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 1

# Upgrade pip
RUN pip install --upgrade pip

# Set workdir
WORKDIR /var/task

# Copy requirements
COPY requirements.txt .

# Install into ./python
RUN pip install -r requirements.txt -t python
