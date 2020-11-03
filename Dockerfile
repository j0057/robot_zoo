FROM j0057.azurecr.io/alpine:3.12

ENV PYTHONUSERBASE=/app

RUN env
RUN apk add python3

RUN python3 -m ensurepip --user

# --> https://github.com/pypa/pip/issues/3969#issuecomment-247381915
RUN echo 'manylinux2010_compatible = True' >/usr/lib/python3.8/site-packages/_manylinux.py

RUN python3 -m pip install \
    --no-cache-dir --disable-pip-version-check --no-warn-script-location --progress-bar off --no-index --find-links /var/lib/python --user \
    --upgrade pip setuptools wheel

RUN python3 -m pip install \
    --no-cache-dir --disable-pip-version-check --no-warn-script-location --progress-bar off --no-index --find-links /var/lib/python --user \
    robot_zoo

CMD python3 -m robot_zoo
