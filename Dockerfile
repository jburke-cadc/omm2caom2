FROM python:3.6-jessie


RUN pip install astropy && pip install numpy && \
        pip install spherical-geometry
RUN pip install cadcdata
RUN pip install matplotlib

RUN oldpath=`pwd` && cd /tmp \
&& wget ftp://heasarc.gsfc.nasa.gov/software/fitsio/c/cfitsio_latest.tar.gz \
&& tar zxvf cfitsio_latest.tar.gz \
&& cd cfitsio \
&& ./configure --prefix=/usr \
&& make -j 2 \
&& make shared \
&& make install \
&& make clean \
&& cd $oldpath \
&& rm -Rf /tmp/cfitsio*
RUN oldpath=`pwd` && cd /tmp \
&& git clone https://github.com/spacetelescope/fitscut \
&& cd fitscut \
&& wget ftp://cfa-ftp.harvard.edu/pub/gsc/WCSTools/wcssubs-3.9.0.tar.gz \
&& tar zxvf wcssubs-3.9.0.tar.gz \
&& mv wcssubs-3.9.0 libwcs \
&& cd libwcs \
&& make \
&& cp libwcs.a /usr/lib \
&& cd .. \
&& ./configure --prefix=/usr \
&& make \
&& make install \
&& make clean \
&& cd $oldpath \
&& rm -Rf /tmp/fitscut*

RUN pip install pyfits
RUN pip install pytest && pip install mock && pip install flake8 && \
        pip install funcsigs && pip install xml-compare && \
        pip install pytest-cov && pip install aenum && pip install future
RUN pip install caom2repo

WORKDIR /usr/src/app
RUN git clone https://github.com/SharonGoliath/caom2tools.git && \
  cd caom2tools && git checkout s2235 && git pull origin s2235 && \
  pip install caom2utils && pip install caom2
RUN git clone https://github.com/SharonGoliath/omm2caom2.git && \
  git checkout s2235 && git pull origin s2235 && \
  pip install omm2caom2

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]

