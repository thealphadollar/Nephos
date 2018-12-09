#!/usr/bin/env bash

NEPHOS_DIR=$(pwd)

if [ $(id -u) -ne 0 ]
    then echo "Error: please launch the script as sudo!"
    exit 1
fi

if [ -z "$0" ]
   then echo "Error: Please Specify either ubuntu or debian"
   exit 1
fi

# install python3
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -y
apt-get install python3.4

if [[ $0 == "ubuntu" ]]
then
    apt-get install python3-pip
else
    # Debian
    easy_install-3.4 pip
fi

echo "python-pip installed"

# install pipenv
if [[ $0 == "ubuntu" ]]
then 
    python3.4 -m pip install pipenv
else
    # Debian
    pip3 install pipenv
fi

export PYTHON_BIN_PATH="$(python3 -m site --user-base)/bin"
export PATH="$PATH:$PYTHON_BIN_PATH"
echo "pipenv installed"

apt-get install -y screen

if [[ $0 == "debian" ]]
then
    apt-get install -y mailx
fi
echo "mail tools installed"

if [[ $0 == "debian" ]]
then
   apt-get installl -y gcc gcc-c++ libx254-devel
fi

apt-get install -y autoconf automake bzip2 cmake libfreetype6-dev git libtool make mercurial pkg-config zlib1g-dev libx264-dev libcairo2-dev libpango1.0-dev libicu-dev
echo "dependencies for building libraries installed"


# install multicat
cd $HOME
git clone --depth 1 https://code.videolan.org/videolan/multicat.git
cd multicat
git clone --depth 1 https://code.videolan.org/videolan/bitstream.git
cd bitstream
make && make install
cd ..
make && make install
echo "multicat installed"

# install tesseract
if [[ $0 == "debian" ]]
    then apt-get install -y leptonica-devel tesseract-devel
else
    then apt-get install -y libtesseract-dev tesseract-ocr
fi

# install basic tesseract language data
wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/fra.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/eng.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/spa.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/rus.traineddata
$('mv *.traineddata /usr/local/share/tessdata')

# install FFMPEG and FFPROBE (https://trac.ffmpeg.org/attachment/wiki/CompilationGuide/Centos/ffmpeg_centos7.sh)
cd $HOME

# Create a temporary directory for sources.
SOURCES=$(mkdir ~/ffmpeg_sources)
cd ~/ffmpeg_sources

# Download the necessary sources.
curl -O http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz
wget http://www.nasm.us/pub/nasm/releasebuilds/2.13.02/nasm-2.13.02.tar.bz2
git clone --depth 1 http://git.videolan.org/git/x264
wget https://bitbucket.org/multicoreware/x265/downloads/x265_2.8.tar.gz
git clone --depth 1 https://github.com/mstorsjo/fdk-aac
curl -O -L http://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz
wget http://www.mirrorservice.org/sites/distfiles.macports.org/libopus/opus-1.2.1.tar.gz
wget https://ftp.osuosl.org/pub/xiph/releases/ogg/libogg-1.3.3.tar.gz
wget http://ftp.osuosl.org/pub/xiph/releases/vorbis/libvorbis-1.3.6.tar.gz
curl -O -L https://ftp.osuosl.org/pub/xiph/releases/theora/libtheora-1.1.1.tar.gz
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git
wget http://ffmpeg.org/releases/ffmpeg-4.0.tar.gz

# Unpack files
for file in $('ls ~/ffmpeg_sources/*.tar.*'); do
tar -xvf ${file}
done

cd nasm-*/
./autogen.sh
./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin"
make
make install
cd ..

cp /root/bin/nasm /usr/bin

cd yasm-*/
./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" && make && make install; cd ..

cp /root/bin/yasm /usr/bin

cd x264/
PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static && make && make install; cd ..

cd /root/ffmpeg_sources/x265_2.8/build/linux
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED:bool=off ../../source && make && make install; cd ~/ffmpeg_sources

cd fdk-aac
autoreconf -fiv && ./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install; cd ..

cd lame-*/
./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --disable-shared --enable-nasm && make && make install; cd ..

cd opus-*/
./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install; cd ..

cd libogg-*/
./configure --prefix="$HOME/ffmpeg_build" --disable-shared && make && make install; cd ..

cd libvorbis-*/
./configure --prefix="$HOME/ffmpeg_build" --with-ogg="$HOME/ffmpeg_build" --disable-shared && make && make install; cd ..

cd libtheora-*/
./configure --prefix="$HOME/ffmpeg_build" --with-ogg="$HOME/ffmpeg_build" --disable-shared && make && make install; cd ..

cd libvpx
./configure --prefix="$HOME/ffmpeg_build" --disable-examples --disable-unit-tests --enable-vp9-highbitdepth --as=yasm && make && make install; cd ..

cd ffmpeg-*/
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --extra-libs=-lpthread --extra-libs=-lm --bindir="$HOME/bin" --enable-gpl --enable-libfdk_aac --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libvorbis --enable-libtheora --enable-libvpx --enable-libx264 --enable-libx265 --enable-nonfree && make && make install && hash -r; cd ..

cd ~/bin
cp ffmpeg ffprobe lame x264 /usr/local/bin

cd /root/ffmpeg_build/bin
cp x265 /usr/local/bin

echo "FFmpeg and FFprobe installed"

# install CCExtractor
cd $HOME
git clone --depth 1 https://github.com/CCExtractor/ccextractor.git
cd ccextractor/linux
./build
ln ./ccextractor /usr/bin/ccextractor
echo "CCExtractor installed"

cd ${NEPHOS_DIR}
pipenv install
pipenv run python3 -m nephos init
