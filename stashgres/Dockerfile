# syntax=docker/dockerfile:1.6
ARG postgresql_major=15

# Extensions release id
ARG pgvector_release=0.5.1
ARG apache_age_release=1.4.0
ARG pgbouncer_release=1.21.0


FROM postgres:15 AS base
ARG postgresql_major

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    bison build-essential flex locales wget libevent-dev pkg-config cmake \
    postgresql-server-dev-$postgresql_major    

ENV LANG=en_US.UTF-8
ENV LC_COLLATE=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8

# Install pgvector extension
WORKDIR /
ARG pgvector_release
ARG pgvector_release_checksum

ADD --checksum=${pgvector_release_checksum} \
    "https://github.com/pgvector/pgvector/archive/refs/tags/v${pgvector_release}.tar.gz" \
    /v${pgvector_release}.tar.gz
RUN tar -xvf v${pgvector_release}.tar.gz -C /tmp && rm -rf v${pgvector_release}.tar.gz

WORKDIR /tmp/pgvector-${pgvector_release}
# TODO: Create debian package instead that can be installed at a later stage
# RUN checkinstall -D --install=no --fstrans=no --backup=no --pakdir=/tmp --nodoc
RUN make clean && make OPTFLAGS="" && make install
RUN mkdir /usr/share/doc/pgvector && \
    cp LICENSE /usr/share/doc/pgvector && \
    rm -r /tmp/pgvector-${pgvector_release}

# Install apache-age extension
WORKDIR /
ARG apache_age_release
ARG apache_age_release_checksum

ADD --checksum=${apache_age_release_checksum} \
    "https://github.com/apache/age/releases/download/PG15%2Fv1.4.0-rc0/apache-age-${apache_age_release}-src.tar.gz" \
    /apache-age-${apache_age_release}-src.tar.gz
RUN tar -xvf apache-age-${apache_age_release}-src.tar.gz -C /tmp && rm -rf apache-age-${apache_age_release}-src.tar.gz

WORKDIR /tmp/apache-age-${apache_age_release}
RUN make && make install
RUN mkdir /usr/share/doc/apache-age && \
    cp LICENSE /usr/share/doc/apache-age && \
    rm -r /tmp/apache-age-${apache_age_release}

# Install pgbouncer extension
WORKDIR /
ARG pgbouncer_release
ARG pgbouncer_release_checksum

ADD --checksum=${pgbouncer_release_checksum} \
    "https://www.pgbouncer.org/downloads/files/1.21.0/pgbouncer-${pgbouncer_release}.tar.gz" \
    /pgbouncer-${pgbouncer_release}.tar.gz
RUN tar -xvf pgbouncer-${pgbouncer_release}.tar.gz -C /tmp && rm -rf pgbouncer-${pgbouncer_release}.tar.gz

WORKDIR /tmp/pgbouncer-${pgbouncer_release}
RUN ./configure --prefix=/usr/local
RUN make -j$(nproc) && make install

RUN mkdir /usr/share/doc/pgbouncer && \
    cp COPYRIGHT /usr/share/doc/apache-age && \
    rm -r /tmp/pgbouncer-${pgbouncer_release}

# # TODO: Install postgrest extension

# Clean up
WORKDIR /
RUN apt-get remove -y build-essential postgresql-server-dev-$postgresql_major && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint-initdb.d/00-create-extension.sql /docker-entrypoint-initdb.d/00-create-extension.sql

# # TODO: run pgbouncer as a non-root user
# # pgbouncer configuration
# RUN mkdir /etc/pgbouncer
# COPY /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/
# COPY /etc/pgbouncer/userlist.txt /etc/pgbouncer/
# # Expose pgbouncer port
# EXPOSE 6432

# # Copy the start script into the container
# COPY entrypoint.sh /usr/local/bin/

# # Ensure executable permissions for the script
# RUN chmod +x /usr/local/bin/entrypoint.sh

# # Set the script as the command to run when the container starts
# CMD ["/usr/local/bin/entrypoint.sh"]

ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=stashgres
ENV POSTGRES_DB=stashgres

CMD ["postgres", "-c", "shared_preload_libraries=vector,age"]