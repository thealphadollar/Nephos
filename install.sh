#!/usr/bin/env bash

if [ `id -u` -ne 0 ]
    then echo "Error: please launch the script as sudo!"
    exit 1
fi

# install python3
yum install -y epel-release
yum install -y python34
echo "Python 3.4 installed"
# install pip3
yum install -y python34-setuptools
easy_install-3.4 pip
echo "python-pip installed"
# install pipenv
pip3 install --user pipenv
echo "pipenv installed"
# install mail
yum install -y mailx
echo "mail tools installed"

# install dependencies for building following libraries
yum install -y autoconf automake bzip2 cmake freetype-devel gcc gcc-c++ git libtool make mercurial pkgconfig zlib-devel x264-devel x254-devel
echo "dependencies for building libraries installed"

# install multicat
cd $HOME
git clone --depth 1 https://code.videolan.org/videolan/multicat.git
cd multicat
make
make install
echo "multicat installed"

# install leptonica
cd $HOME
wget http://www.leptonica.org/source/leptonica-1.76.0.tar.gz
tar xzvf leptonica-1.76.0.tar.gz
rm leptonica-1.76.0.tar.gz
cd leptonica-1.76.0
./configure & make & make install
echo "leptonica installed"

# install tesseract
cd $HOME
wget https://github.com/tesseract-ocr/tesseract/archive/3.05.02.tar.gz
tar xvzf 3.05.02.tar.gz
rm 3.05.02.tar.gz
cd tesseract-3.05.02
./autogen.sh
./configure
make & make install
ldconfig
echo "tesseract-ocr installed"

# install FFMPEG and FFPROBE (https://trac.ffmpeg.org/attachment/wiki/CompilationGuide/Centos/ffmpeg_centos7.sh)
cd $HOME
# Install yasm from repos

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
for file in `ls ~/ffmpeg_sources/*.tar.*`; do
tar -xvf $file
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
./autogen.sh
./configure
make && make install
echo "CCExtractor installed"

# install Nephos python dependencies
pipenv install