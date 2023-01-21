FROM alpine
COPY ./app /app

WORKDIR /app

#RUN apk --no-cache add curl tar yasm ffmpeg tzdata &&\
RUN chmod +x go-cqhttp

CMD ["/bin/sh"]
#WORKDIR /data
ENTRYPOINT exec /app/go-cqhttp faststart

