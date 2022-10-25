ARG debian_buster_image_tag=8-jre-slim
FROM openjdk:${debian_buster_image_tag}

ARG shared_workspace=/opt/workspace
ENV SHARED_WORKSPACE=${shared_workspace}

# OS + Python 3.9
RUN mkdir -p ${shared_workspace} && \
    apt-get update -y && \
    apt-get install -y python3 && \
    ln -s /usr/bin/python3.9 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# -- Runtime
VOLUME ${shared_workspace}
CMD ["bash"]