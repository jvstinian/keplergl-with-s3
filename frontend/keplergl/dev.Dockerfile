FROM node:14-alpine

WORKDIR /opt/keplergl-web

VOLUME /opt/keplergl-web

ENV PORT=8000

ENTRYPOINT ["yarn", "start"]

EXPOSE 8000

