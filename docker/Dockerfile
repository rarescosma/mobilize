# Use a fixed alpine:edge tag as a base and install our dependencies:
# - calibre for `ebook-convert` (will also give use python3.12)
# - nodejs + npm for the Readability wrapper
# - watchexec for watch support
#
# Removing `/usr/lib/python3.12/EXTERNALLY-MANAGED` and installing
# python packages as root feels a bit hacky and cursed, but we
# couldn't be bothered with the virtual environment dance.
#
# We're also manually nuking a Qt6 library that appears unused by
# the `ebook-convert` utility, just to dampen the hit of calibre
# barfing a 900M layer into the image.
ARG HUB=docker.io
FROM ${HUB}/library/alpine:20240807

WORKDIR /mobilize
COPY package.json package-lock.json requirements.txt /mobilize/

RUN set -eux; \
    echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories ; \
    apk update; apk add --no-cache calibre nodejs npm watchexec ; \
    npm install --cache /tmp/no-cache; rm -rf /tmp/no-cache ; \
    rm -f /usr/lib/python3.12/EXTERNALLY-MANAGED ; \
    python3 -m ensurepip ; \
    pip3 install --no-cache-dir --root-user-action=ignore -r requirements.txt ; \
    rm -f /usr/lib/libQt6WebEngineCore.so.6.7.2


ENV NODE_NO_WARNINGS=1

COPY extract_article.js setup.py watcher.sh /mobilize/
COPY mobilize /mobilize/mobilize

RUN pip3 install --root-user-action=ignore -e .

ENTRYPOINT ["/mobilize/watcher.sh"]
