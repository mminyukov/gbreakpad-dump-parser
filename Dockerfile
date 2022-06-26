FROM ubuntu:20.04 AS build
WORKDIR /opt
RUN apt-get update && apt-get install -y python python3 git curl wget build-essential gcc g++ \
  && git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git \
  && export PATH="/opt/depot_tools:$PATH" \
  && mkdir -p /opt/breakpad && cd /opt/breakpad && fetch breakpad \
  && cd /opt/breakpad/src && ./configure && make && mkdir result && make install DESTDIR=./result/ \
  && cd /opt && tar zcf result.tgz -C /opt/breakpad/src/result .

FROM python:3.10-slim
WORKDIR /gbreakpad-dump-parser

COPY --from=build /opt/result.tgz .
RUN pip3 install flask waitress \
  && tar xf result.tgz -C / \
  && rm result.tgz

COPY gbreakpad-dump-parser/ .

CMD ["python3","-u","main.py"]
