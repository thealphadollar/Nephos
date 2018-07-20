install:
	# install python3
	sudo yum install -y epel-release
	sudo yum install -y python34
	# install pip3
	sudo yum install -y python34-setuptools
	sudo easy_install-3.4 pip
	# install pipenv
	pip3 install --user pipenv
	# install mail
	sudo yum install mailx
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
