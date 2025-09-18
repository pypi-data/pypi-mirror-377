# CELN Sidecar Service Dockerfile

FROM python:3.11-slim
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"
# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gnupg \
    openssh-client \
    curl \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY sidecar/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sidecar/src/ ./src/

# Copy entrypoint script
COPY docker/sidecar/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create a non-root user
RUN useradd --create-home --shell /bin/bash $NB_USER
RUN chown -R $NB_USER:$NB_USER /app

# Give jovyan sudo permissions for specific directory ownership commands
RUN echo "$NB_USER ALL=(ALL) NOPASSWD: /bin/chown -R jovyan\\:jovyan /tmp/.git-metadata" >> /etc/sudoers && \
    echo "$NB_USER ALL=(ALL) NOPASSWD: /bin/chown -R jovyan\\:jovyan /tmp/work" >> /etc/sudoers

# Switch to non-root user
USER $NB_USER

# Mark directories as safe for git to handle ownership mismatches in Docker
# RUN git config --global --add safe.directory /tmp && \
#     git config --global --add safe.directory /workspace

# Expose port
EXPOSE 8001

# Set entrypoint to fix permissions and start application
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
