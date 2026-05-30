ARG PYTHON_IMAGE=python:3.12-slim

FROM ${PYTHON_IMAGE} AS requirements_export
WORKDIR /build

RUN pip install --no-cache-dir "poetry>=2.0.0,<3.0.0" "poetry-plugin-export>=1.0.0,<2.0.0"
COPY pyproject.toml poetry.lock ./
RUN poetry export -o requirements.txt

FROM ${PYTHON_IMAGE} AS requirements_builder
WORKDIR /build
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -U pip
COPY --from=requirements_export /build/requirements.txt /build/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /build/requirements.txt

FROM ${PYTHON_IMAGE} AS runtime
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH="/app"

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid app --shell /bin/bash --create-home app

COPY --chown=10001:10001 scripts/init.sh /app/init.sh
RUN chmod +x /app/init.sh
COPY --chown=10001:10001 scripts/ /app/scripts
COPY --chown=10001:10001 --from=requirements_builder /opt/venv /opt/venv
COPY --chown=10001:10001 src/ /app/src
COPY --chown=10001:10001 alembic.ini /app/alembic.ini
COPY --chown=10001:10001 alembic/ /app/alembic

USER 10001:10001

EXPOSE 8000
ENTRYPOINT ["/app/init.sh"]
