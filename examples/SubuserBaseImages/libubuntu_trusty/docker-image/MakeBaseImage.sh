#!/usr/bin/env bash
# based on: https://github.com/dotcloud/docker/tree/master/contrib/mkimage-debootstrap.sh
set -e
SCRIPTPATH="$( cd "$( echo "${BASH_SOURCE[0]%/*}" )" && pwd )"

#================ CONFIG HERE FOR DIFFERENT VERSIONS
variant='minbase'
include='iproute,iputils-ping'
arch='amd64'

repo="subuser-libubuntu_trusty"
# these should match the names found at http://www.debian.org/releases/
# this should match the name found at http://releases.ubuntu.com/
# see also: debootstrap/scripts links
suite="trusty"

#Debian unstable
debianUnstable="sid"

# stick to the default debootstrap mirror if one is not provided
mirror= 

#empty or 1 for just create a tarball, especially for dockerbrew (uses repo as tarball name)
justTar=

#================ END CONFIG HERE FOR DIFFERENT VERSIONS
cd "$SCRIPTPATH/debootstrap-1.0.59"
sudo make clean
sudo make devices.tar.gz
cd "$SCRIPTPATH"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# some rudimentary detection for whether we need to "sudo" our docker calls
docker=''
if docker version > /dev/null 2>&1; then
 docker='docker'
elif sudo docker version > /dev/null 2>&1; then
 docker='sudo docker'
elif command -v docker > /dev/null 2>&1; then
 docker='docker'
else
 echo >&2 "warning: either docker isn't installed, or your current user cannot run it;"
 echo >&2 "         this script is not likely to work as expected"
 sleep 3
 docker='docker' # give us a command-not-found later
fi

# make sure we have an absolute path to our final tarball so we can still reference it properly after we change directory
if [ "$justTar" ]; then
 if [ ! -d "$(dirname "$repo")" ]; then
  echo >&2 "error: $(dirname "$repo") does not exist"
  exit 1
 fi
 repo="$(cd "$(dirname "$repo")" && pwd -P)/$(basename "$repo")"
fi


target="$SCRIPTPATH/docker-debootstrap-$suite"

cd "$(dirname "$(readlink -f "$BASH_SOURCE")")"
returnTo="$(pwd -P)"


set -x

# bootstrap
sudo rm -rf "$target"
sudo mkdir -p "$target"
sudo http_proxy=$http_proxy $SCRIPTPATH/debootstrap-1.0.59/debootstrap --verbose --variant="$variant" --include="$include" --arch="$arch" "$suite" "$target" "$mirror"

cd "$target"


# prevent init scripts from running during install/update
#  policy-rc.d (for most scripts)
echo $'#!/bin/sh\nexit 101' | sudo tee usr/sbin/policy-rc.d > /dev/null
sudo chmod +x usr/sbin/policy-rc.d
#  initctl (for some pesky upstart scripts)
sudo chroot . dpkg-divert --local --rename --add /sbin/initctl
sudo ln -sf /bin/true sbin/initctl
# see https://github.com/dotcloud/docker/issues/446#issuecomment-16953173

# shrink the image, since apt makes us fat (wheezy: ~157.5MB vs ~120MB)
sudo chroot . apt-get clean

if strings usr/bin/dpkg | grep -q unsafe-io; then
 # while we're at it, apt is unnecessarily slow inside containers
 #  this forces dpkg not to call sync() after package extraction and speeds up install
 #    the benefit is huge on spinning disks, and the penalty is nonexistent on SSD or decent server virtualization
 echo 'force-unsafe-io' | sudo tee etc/dpkg/dpkg.cfg.d/02apt-speedup > /dev/null
 # we have this wrapped up in an "if" because the "force-unsafe-io"
 # option was added in dpkg 1.15.8.6
 # (see http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=584254#82),
 # and ubuntu lucid/10.04 only has 1.15.5.6
fi

# we want to effectively run "apt-get clean" after every install to keep images small (see output of "apt-get clean -s" for context)
{
 aptGetClean='"rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true";'
 echo "DPkg::Post-Invoke { ${aptGetClean} };"
 echo "APT::Update::Post-Invoke { ${aptGetClean} };"
 echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";'
} | sudo tee etc/apt/apt.conf.d/no-cache > /dev/null

# and remove the translations, too
echo 'Acquire::Languages "none";' | sudo tee etc/apt/apt.conf.d/no-languages > /dev/null

# helpful undo lines for each the above tweaks (for lack of a better home to keep track of them):
#  rm /usr/sbin/policy-rc.d
#  rm /sbin/initctl; dpkg-divert --rename --remove /sbin/initctl
#  rm /etc/dpkg/dpkg.cfg.d/02apt-speedup
#  rm /etc/apt/apt.conf.d/no-cache
#  rm /etc/apt/apt.conf.d/no-languages



# see also rudimentary platform detection in hack/install.sh
lsbDist=''
if [ -r etc/lsb-release ]; then
 lsbDist="$(. etc/lsb-release && echo "$DISTRIB_ID")"
fi
if [ -z "$lsbDist" ] && [ -r etc/debian_version ]; then
 lsbDist='Debian'
fi

case "$lsbDist" in
 Debian)
  # add the updates and security repositories
  if [ "$suite" != "$debianUnstable" -a "$suite" != 'unstable' ]; then
   # ${suite}-updates only applies to non-unstable
   sudo sed -i "p; s/ $suite main$/ ${suite}-updates main/" etc/apt/sources.list
   
   # same for security updates
   echo "deb http://security.debian.org/ $suite/updates main" | sudo tee -a etc/apt/sources.list > /dev/null
  fi
  ;;
 Ubuntu)
  # add the universe, updates, and security repositories
  sudo sed -i "
   s/ $suite main$/ $suite main universe/; p;
   s/ $suite main/ ${suite}-updates main/; p;
   s/ $suite-updates main/ ${suite}-security main/
  " etc/apt/sources.list
  ;;
esac


# make sure our packages lists are as up to date as we can get them
sudo chroot . apt-get update

if [ "$justTar" ]; then
 # create the tarball file so it has the right permissions (ie, not root)
 sudo touch "$repo"
 
 # fill the tarball
 sudo tar --numeric-owner -caf "$repo" .
else
 # create the image (and tag $repo:latest)
 sudo tar --numeric-owner -c . | $docker import - $repo:latest
 
 # test the image
 $docker run -i -t $repo:latest echo success
fi

# ================ cleanup
cd "$SCRIPTPATH/debootstrap-1.0.59"
sudo rm -rf devices.tar.gz
cd "$SCRIPTPATH"
sudo rm -rf "$target"
