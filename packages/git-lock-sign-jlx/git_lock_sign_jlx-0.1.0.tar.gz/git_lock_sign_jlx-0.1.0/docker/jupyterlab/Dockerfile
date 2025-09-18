ARG BASE_CONTAINER=polusai/notebook:2.1.3
FROM $BASE_CONTAINER

LABEL maintainer="JupyterLab Extension"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy source code
COPY . /opt/app/

# Environment variables
ENV XDG_CACHE_HOME="/home/$NB_USER/.cache/"
ENV PS1="\u $ "

USER root

# Install apt packages
RUN apt-fast update && \
    apt-fast install -yq --no-install-recommends fonts-liberation pandoc run-one curl git tzdata unzip openssh-client less texlive-xetex texlive-fonts-recommended texlive-plain-generic xclip emacs inkscape libsm6 libxext-dev libxrender1 lmodern ffmpeg ssh procps libicu-dev rsync screen && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID
WORKDIR /tmp

# Install conda packages
RUN mamba install --yes \
    jupyter_core \
    notebook=7.3.2 \
    nbclassic=1.1.0 \
    jupyter_server=2.15.0 \
    jupyterlab=4.3.5 \
    jupyterhub=5.1.0 \
    jupyterlab-git=0.50.1 \
    jupyterlab-latex=4.1.4 \
    jupyterlab-myst=2.4.2 \
    jupyter-archive=3.4.0 \
    jupyter-ai=2.22.0 \
    jupyter-resource-usage=1.1.0 \
    jupyterlab-tour=4.0.1 \
    jupyterlab-lsp=5.1.0 \
    python-lsp-server=1.11.0 \
    papermill=2.6.0 \
    numexpr=2.10.0 \
    matplotlib-base=3.9.2 \
    scipy=1.14.0 \
    feather-format=0.4.1 \
    nbformat=5.10.4 \
    sos-notebook=0.24.4 \
    jupyterlab-sos=0.10.4 \
    sos-papermill=0.2.1 \
    sos-python=0.20.2 \
    nbdime=4.0.1 \
    ipywidgets=8.1.5 \
    python-kubernetes=29.0.0 \
    yarn \
    nodejs=18.20.5 \
    copier=9.3.1 \
    jinja2-time=0.2.0 \
    typing-extensions=4.12.2 \
    jinja2=3.1.5 \
    panel=1.4.5 \
    texlab=5.19.0 \
    chktex=1.7.9 \
    stackview=0.9.2 \
    configobj=5.0.8 \
    pydantic=2.8.2 \
    pyyaml=6.0.2 \
    awscli=2.17.44 \
    jupyterlab_templates=0.5.2 \
    jupysql=0.10.12 \
    jupyterlab-spreadsheet-editor=0.7.2 \
    voila=0.5.7 && \
    pip install jupyterlab-polus-render==1.0.1 jhoauthrefresh==0.3.0 dock8r==0.1.3 imjoy-jupyterlab-extension==0.2.6 jupyter-collaboration==3.1.0 && \
    jupyter server --generate-config -y && \
    mamba clean --all -f -y && \
    npm cache clean --force && \
    jupyter lab clean && \
    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete && \
    fix-permissions "${CONDA_DIR}"

# Installation scripts
RUN jupyter server extension enable jhoauthrefresh
RUN rm -rf /tmp/jupyter-lmod && \
    git clone https://github.com/cmd-ntrf/jupyter-lmod.git /tmp/jupyter-lmod && \
    cd /tmp/jupyter-lmod && \
    git switch jupyterlab4 && \
    echo "enableImmutableInstalls: false" > .yarnrc.yml && \
    echo "nodeLinker: node-modules" >> .yarnrc.yml && \
    pip install .
# Build our extension (needs root permissions)
USER root
RUN chown -R ${NB_UID}:${NB_GID} /opt/app
USER $NB_UID
RUN set -e && \
    cd /opt/app && \
    echo "📂 Current directory: $(pwd)" && \
    echo "📋 Directory contents:" && \
    ls -la && \
    echo "📦 Installing dependencies..." && \
    jlpm install && \
    echo "🔨 Building extension..." && \
    jlpm build && \
    echo "📋 Checking if lib directory exists..." && \
    if [ -d "lib" ]; then \
      echo "✅ lib directory found:" && \
      ls -la lib/; \
    else \
      echo "❌ lib directory not found!"; \
      exit 1; \
    fi && \
    echo "📋 Checking package.json..." && \
    cat package.json | grep -A5 -B5 "jupyterlab" && \
    echo "🔌 Installing extension in develop mode..." && \
    pip install -e . && \
    echo "📋 Listing installed extensions..." && \
    jupyter labextension list

# Configuration files
USER root
COPY docker/jupyterlab/temp_mito-config /home/jovyan/.mito/user.json
RUN chmod 775 /home/jovyan/.mito/user.json
COPY docker/jupyterlab/temp_start-notebook.sh /usr/local/bin/start-notebook.sh
RUN chmod 775 /usr/local/bin/start-notebook.sh
COPY docker/jupyterlab/temp_start-notebook.py /usr/local/bin/start-notebook.py
RUN chmod 775 /usr/local/bin/start-notebook.py
COPY docker/jupyterlab/temp_start-singleuser.sh /usr/local/bin/start-singleuser.sh
RUN chmod 775 /usr/local/bin/start-singleuser.sh
COPY docker/jupyterlab/temp_start-singleuser.py /usr/local/bin/start-singleuser.py
RUN chmod 775 /usr/local/bin/start-singleuser.py
COPY docker/jupyterlab/temp_jupyter_server_config.py /etc/jupyter/jupyter_server_config.py
RUN chmod 775 /etc/jupyter/jupyter_server_config.py
COPY docker/jupyterlab/temp_docker_healthcheck.py /etc/jupyter/docker_healthcheck.py
RUN chmod 775 /etc/jupyter/docker_healthcheck.py
RUN fix-permissions /etc/jupyter/

# Final setup
RUN chown -R ${NB_UID}:${NB_GID} /opt/app
ENV PS1="\u $ "
RUN touch ~/.hushlogin

USER $NB_UID
EXPOSE 8888

HEALTHCHECK --interval=3s --timeout=1s --start-period=3s --retries=3 \
    CMD /etc/jupyter/docker_healthcheck.py || exit 1

USER root
RUN rm -rf "${HOME}/.cache" "${HOME}/.yarn"
USER $NB_UID

CMD ["start-notebook.py"]