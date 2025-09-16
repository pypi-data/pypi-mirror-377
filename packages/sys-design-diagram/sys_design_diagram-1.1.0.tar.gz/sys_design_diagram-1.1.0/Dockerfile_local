# syntax=docker/dockerfile:1

# Base stage
FROM python:3.12-slim AS base
LABEL maintainer="Aydin A."

# Set environment variables
ENV USER_NAME=sdd-user
ENV GROUP_NAME=sdd-group
ENV HOME=/home/$USER_NAME
ENV PATH="$HOME/.local/bin:$PATH"

# Set the working directory
WORKDIR $HOME

# Create a non-root user and group
RUN groupadd -r $GROUP_NAME && \
    useradd -r -g $GROUP_NAME -d $HOME -s /bin/bash $USER_NAME && \
    mkdir -p $HOME/.local/bin && \
    chown -R $USER_NAME:$GROUP_NAME /home/$USER_NAME

# Builder stage
FROM base AS builder

# Install dependencies for building the package
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the non-root user
USER $USER_NAME

# Cache pip installations
COPY --chown=$USER_NAME:$GROUP_NAME requirements.txt .

# Copy the local files into the container
COPY --chown=$USER_NAME:$GROUP_NAME . .

# Install the dependencies and build the package
RUN pip install --user --upgrade pip && \
    pip install --user -r requirements.txt && \
    pip install --user hatch && \
    hatch build -t wheel && \
    pip install --user dist/*.whl && \
    rm -rf dist

# Final stage
FROM base AS final

# Set the working directory
WORKDIR $HOME

ARG IMAGE_NAME="sys-design-diagram"
ARG IMAGE_VERSION="latest"
ARG IMAGE_AUTHOR="Aydin A."
ARG IMAGE_LICENSE="MIT"
ARG IMAGE_DESCRIPTION="System Design Diagram Generator"
ARG BUILD_DATE
ARG GIT_COMMIT

ENV IMAGE_NAME="${IMAGE_NAME}"
ENV IMAGE_VERSION="${IMAGE_VERSION}"
ENV IMAGE_AUTHOR="${IMAGE_AUTHOR}"
ENV IMAGE_LICENSE="${IMAGE_LICENSE}"
ENV IMAGE_DESCRIPTION="${IMAGE_DESCRIPTION}"

LABEL org.opencontainers.image.title="${IMAGE_NAME}" \
      org.opencontainers.image.description="${IMAGE_DESCRIPTION}" \
      org.opencontainers.image.authors="${IMAGE_AUTHOR}" \
      org.opencontainers.image.licenses="${IMAGE_LICENSE}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.url="https://github.com/aydabd/sys-design-diagram" \
      org.opencontainers.image.documentation="https://github.com/aydabd/sys-design-diagram/blob/main/README.rst" \
      org.opencontainers.image.source="https://github.com/aydabd/sys-design-diagram" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

# Install runtime dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends plantuml graphviz && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the non-root user
USER $USER_NAME

# Copy the installed dependencies from the builder image
COPY --from=builder --chown=$USER_NAME:$GROUP_NAME $HOME/.local $HOME/.local

# Expose the output directory as a volume
VOLUME $HOME/sdd-outputs

# Set the entrypoint to the installed package which will create the diagrams in output directory
ENTRYPOINT ["sys-design-diagram"]

# Set the default command to show the help message
CMD ["--help"]

