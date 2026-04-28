# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY portal/requirements.txt /app/portal/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip \
	&& python3 -m pip install --no-cache-dir -r /app/portal/requirements.txt

COPY portal /app/portal

RUN chmod +x /app/portal/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/portal/entrypoint.sh"]
