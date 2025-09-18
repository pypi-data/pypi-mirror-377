#!/usr/bin/env python3
"""
Build Dockerfile from base.yaml and values.yaml without complex templating
"""
import yaml
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Build Dockerfile from config')
    parser.add_argument('--values', required=True, help='Values YAML file path')
    parser.add_argument('--base', required=True, help='Base YAML file path')
    parser.add_argument('--output', required=True, help='Output Dockerfile path')
    
    args = parser.parse_args()
    
    # Load configs
    with open(args.values, 'r') as f:
        values = yaml.safe_load(f)
    
    with open(args.base, 'r') as f:
        base_config = yaml.safe_load(f)
    
    # Start building Dockerfile
    dockerfile_lines = []
    temp_files_created = []
    
    # Base image
    dockerfile_lines.append(f"ARG BASE_CONTAINER={base_config['base']}")
    dockerfile_lines.append("FROM $BASE_CONTAINER")
    dockerfile_lines.append("")
    dockerfile_lines.append("LABEL maintainer=\"JupyterLab Extension\"")
    dockerfile_lines.append("")
    
    # Shell configuration
    dockerfile_lines.append("SHELL [\"/bin/bash\", \"-o\", \"pipefail\", \"-c\"]")
    dockerfile_lines.append("")
    
    # Copy source code
    dockerfile_lines.append("# Copy source code")
    dockerfile_lines.append("COPY . /opt/app/")
    dockerfile_lines.append("")
    
    # Environment variables
    if 'env' in values:
        dockerfile_lines.append("# Environment variables")
        for env_item in values['env']:
            if isinstance(env_item, dict):
                for key, value in env_item.items():
                    dockerfile_lines.append(f"ENV {key}=\"{value}\"")
        dockerfile_lines.append("")
    
    # Switch to root for package installation
    dockerfile_lines.append("USER root")
    dockerfile_lines.append("")
    
    # Install apt packages
    if 'apt' in values and values['apt']:
        dockerfile_lines.append("# Install apt packages")
        apt_packages = []
        for item in values['apt']:
            if isinstance(item, str):
                apt_packages.append(item)
            elif isinstance(item, dict):
                for key in item.keys():
                    apt_packages.append(key)
        
        dockerfile_lines.append("RUN apt-fast update && \\")
        dockerfile_lines.append(f"    apt-fast install -yq --no-install-recommends {' '.join(apt_packages)} && \\")
        dockerfile_lines.append("    apt-get clean && \\")
        dockerfile_lines.append("    rm -rf /var/lib/apt/lists/*")
        dockerfile_lines.append("")
    
    # Switch to jovyan user
    dockerfile_lines.append("USER $NB_UID")
    dockerfile_lines.append("WORKDIR /tmp")
    dockerfile_lines.append("")
    
    # Install conda packages
    if 'conda' in values and values['conda']:
        dockerfile_lines.append("# Install conda packages")
        conda_packages = []
        for item in values['conda']:
            if isinstance(item, str):
                conda_packages.append(item)
            elif isinstance(item, dict):
                for key, value in item.items():
                    if value:
                        # Quote the package spec if it contains special characters
                        if any(char in str(value) for char in ['>', '<', '=', ',']):
                            conda_packages.append(f'"{key}={value}"')
                        else:
                            conda_packages.append(f"{key}={value}")
                    else:
                        conda_packages.append(key)
        
        dockerfile_lines.append("RUN mamba install --yes \\")
        for i, pkg in enumerate(conda_packages):
            if i == len(conda_packages) - 1:
                dockerfile_lines.append(f"    {pkg} && \\")
            else:
                dockerfile_lines.append(f"    {pkg} \\")
        
        # Add pip packages if any
        if 'pip' in values and values['pip']:
            pip_packages = []
            for item in values['pip']:
                if isinstance(item, str):
                    pip_packages.append(item)
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if value:
                            pip_packages.append(f"{key}=={value}")
                        else:
                            pip_packages.append(key)
            
            dockerfile_lines.append(f"    pip install {' '.join(pip_packages)} && \\")
        
        dockerfile_lines.append("    jupyter server --generate-config -y && \\")
        dockerfile_lines.append("    mamba clean --all -f -y && \\")
        dockerfile_lines.append("    npm cache clean --force && \\")
        dockerfile_lines.append("    jupyter lab clean && \\")
        dockerfile_lines.append("    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \\")
        dockerfile_lines.append("    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \\")
        dockerfile_lines.append("    find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete && \\")
        dockerfile_lines.append("    fix-permissions \"${CONDA_DIR}\"")
        dockerfile_lines.append("")
    
    # Run scripts
    if 'scripts' in values and values['scripts']:
        dockerfile_lines.append("# Installation scripts")
        for script_item in values['scripts']:
            if isinstance(script_item, dict):
                for name, content in script_item.items():
                    # Special handling for our extension build script - needs root permissions first
                    if name == 'build-git-lock-sign-extension':
                        dockerfile_lines.append("# Build our extension (needs root permissions)")
                        dockerfile_lines.append("USER root")
                        dockerfile_lines.append("RUN chown -R ${NB_UID}:${NB_GID} /opt/app")
                        dockerfile_lines.append("USER $NB_UID")
                        
                    # The script content already has proper line continuations, just wrap in RUN
                    lines = content.strip().split('\n')
                    if len(lines) == 1:
                        dockerfile_lines.append(f"RUN {lines[0]}")
                    else:
                        # Don't add extra backslashes - the content already has them
                        dockerfile_lines.append(f"RUN {lines[0]}")
                        for line in lines[1:]:
                            dockerfile_lines.append(f"    {line}")
        dockerfile_lines.append("")
    
    # Create configuration files using temporary files and COPY
    if 'addfiles' in values:
        dockerfile_lines.append("# Configuration files")
        dockerfile_lines.append("USER root")
        
        for file_item in values['addfiles']:
            if isinstance(file_item, dict):
                for name, config in file_item.items():
                    if config.get('source') != '.':  # Skip the source copy, already done
                        dest = config['destination']
                        content = config['source']
                        
                        # Create temporary file
                        temp_file_name = f"temp_{name}"
                        temp_file_path = Path(args.output).parent / temp_file_name
                        with open(temp_file_path, 'w') as tf:
                            tf.write(content)
                        temp_files_created.append(temp_file_path)
                        
                        # Use COPY - copy temp file to actual destination with proper filename
                        if dest.endswith('/'):
                            # Destination is a directory, append the actual filename
                            actual_dest = f"{dest}{name}"
                        else:
                            # Destination is a full file path
                            actual_dest = dest
                        
                        # Adjust the COPY source path for Docker build context
                        # Build context is parent directory, so temp files are at docker/jupyterlab/temp_*
                        docker_temp_path = f"docker/jupyterlab/{temp_file_name}"
                        dockerfile_lines.append(f"COPY {docker_temp_path} {actual_dest}")
                        if 'permissions' in config:
                            dockerfile_lines.append(f"RUN chmod {config['permissions']} {actual_dest}")
        
        dockerfile_lines.append("RUN fix-permissions /etc/jupyter/")
        dockerfile_lines.append("")
    
    # Final setup
    dockerfile_lines.append("# Final setup")
    dockerfile_lines.append("RUN chown -R ${NB_UID}:${NB_GID} /opt/app")
    dockerfile_lines.append("ENV PS1=\"\\u $ \"")
    dockerfile_lines.append("RUN touch ~/.hushlogin")
    dockerfile_lines.append("")
    dockerfile_lines.append("USER $NB_UID")
    dockerfile_lines.append("EXPOSE 8888")
    dockerfile_lines.append("")
    dockerfile_lines.append("HEALTHCHECK --interval=3s --timeout=1s --start-period=3s --retries=3 \\")
    dockerfile_lines.append("    CMD /etc/jupyter/docker_healthcheck.py || exit 1")
    dockerfile_lines.append("")
    dockerfile_lines.append("USER root")
    dockerfile_lines.append("RUN rm -rf \"${HOME}/.cache\" \"${HOME}/.yarn\"")
    dockerfile_lines.append("USER $NB_UID")
    dockerfile_lines.append("")
    dockerfile_lines.append("CMD [\"start-notebook.py\"]")
    
    # Write the Dockerfile
    with open(args.output, 'w') as f:
        f.write('\n'.join(dockerfile_lines))
    
    # Don't clean up temporary files - they're needed for Docker build
    # The Makefile will clean them up after the build
    if temp_files_created:
        print(f"Generated {args.output} with {len(temp_files_created)} temporary files")
        print("Temporary files (will be cleaned up after build):")
        for temp_file in temp_files_created:
            print(f"  {temp_file}")
    else:
        print(f"Generated {args.output}")

if __name__ == '__main__':
    main() 