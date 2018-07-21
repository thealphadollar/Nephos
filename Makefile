install:
	# install python3
	yum install -y epel-release
	yum install -y python34
	# install pip3
	yum install -y python34-setuptools
	easy_install-3.4 pip
	# install pipenv
	pip3 install --user pipenv
	# install mail
	yum install mailx
	# install multicat
	cd ~
	git clone https://code.videolan.org/videolan/multicat.git
	cd multicat
	make	
	# install FFMPEG/FFPROBE
	rpm --import http://packages.atrpms.net/RPM-GPG-KEY.atrpms
	echo "[atrpms] \
	name=Fedora Core $releasever - $basearch - ATrpms \
	baseurl=http://dl.atrpms.net/el$releasever-$basearch/atrpms/stable \
	gpgkey=http://ATrpms.net/RPM-GPG-KEY.atrpms \
	enabled=1 \
	gpgcheck=1" >> /etc/yum.repos.d/atrpms.repo
	yum install ffmpeg ffmpeg-devel
	# install CCEx
	yum install gcc-c++
	yum install curl-devel
	# install tesseract and leptonica
	cd /opt
	
	yum -y update 
	yum -y install libstdc++ autoconf automake libtool autoconf-archive \
	pkg-config gcc gcc-c++ make libjpeg-devel libpng-devel libtiff-devel \
	zlib-devel
	# Install AutoConf-Archive
	wget ftp://mirror.switch.ch/pool/4/mirror/epel/7/ppc64/a/autoconf-archive-2016.09.16-1.el7.noarch.rpm
	rpm -i autoconf-archive-2016.09.16-1.el7.noarch.rpm
	# Install Leptonica from Source
	wget http://www.leptonica.com/source/leptonica-1.75.3.tar.gz
	tar -zxvf leptonica-1.75.3.tar.gz
	cd leptonica-1.75.3
	./autobuild
	./configure
	make
	make install
	cd ..
	# Install Tesseract from Source
	wget https://github.com/tesseract-ocr/tesseract/archive/3.05.01.tar.gz
	tar -zxvf 3.05.01.tar.gz
	cd tesseract-3.05.01
	./autogen.sh
	PKG_CONFIG_PATH=/usr/local/lib/pkgconfig LIBLEPT_HEADERSDIR=/usr/local/include ./configure --with-extra-includes=/usr/local/include --with-extra-libraries=/usr/local/lib
	LDFLAGS="-L/usr/local/lib" CFLAGS="-I/usr/local/include" make
	make install
	ldconfig
	cd ..
	# Download and install tesseract language files
	wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/fra.traineddata
	wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/spa.traineddata
	wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/eng.traineddata
	mv *.traineddata /usr/local/share/tessdata
	ln -s /opt/tesseract-3.05.01 /opt/tesseract-latest
	# install all python dependencies and create virtual environment
	pipenv install

clean:
	rm -r ~/Nephos

# Commands beyond this concern Travis CI and should
# only be launched from within Travis environment

travis_install:    
	pip install pipenv
	pipenv install --dev

travis_test:
	pipenv run py.test --cov=./

travis_after_success:
	# TODO: Add instruction to push to pypi
	pipenv run codecov
