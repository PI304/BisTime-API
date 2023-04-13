FROM python:3.10

COPY ./ /home/bistime/

WORKDIR /home/bistime/

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY ./entrypoint.sh /
RUN chmod 747 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#CMD ["bash", "-c", "python3 manage.py migrate && gunicorn config.wsgi.deploy:application --bind 0.0.0.0:8080 --timeout=30"]