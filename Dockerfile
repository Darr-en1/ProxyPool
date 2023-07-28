FROM python:3.11

ARG app_env=prod

ENV TZ=Asia/Shanghai \
    APP_ENV=$app_env

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5555
ENTRYPOINT ["supervisord", "-c", "supervisord.conf"]
