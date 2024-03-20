FROM node:14-alpine

WORKDIR /opt/keplergl-web

VOLUME /opt/keplergl-web

ENV PORT=8000
ENV HOST=0.0.0.0
# ENV DANGEROUSLY_DISABLE_HOST_CHECK=true

ENTRYPOINT ["yarn", "start"]

EXPOSE 8000

