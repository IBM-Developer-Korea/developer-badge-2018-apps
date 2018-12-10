#!/bin/bash

FSBIN=fatfs.bin
DEFAULT_APPS="netconfig home"

mcopy -V > /dev/null || {
	echo "Install mtools to create FAT filesystem image"
	exit 1
}

# Create empty FAT filesystem
dd if=/dev/zero of=${FSBIN} bs=64k count=32

# Boot sector and first entry for FAT
echo -n -e \\xeb\\xfe\\x90\\x4d\\x53\\x44\\x4f\\x53\
\\x35\\x2e\\x30\\x00\\x10\\x01\\x01\\x00\
\\x01\\x00\\x02\\x00\\x02\\xf8\\x01\\x00\
\\x3f\\x00\\xff\\x00\\x00\\x00\\x00\\x00\
\\x00\\x00\\x00\\x00\\x80\\x00\\x29\\x00\
\\x00\\x21\\x28\\x4e\\x4f\\x20\\x4e\\x41\
\\x4d\\x45\\x20\\x20\\x20\\x20\\x46\\x41\
\\x54\\x20\\x20\\x20\\x20\\x20\\x00\\x00| \
dd of=${FSBIN} conv=notrunc

echo -n -e \\x55\\xaa | \
dd of=${FSBIN} conv=notrunc bs=1 seek=510

echo -n -e \\xf8\\xff\\xff | \
dd of=${FSBIN} conv=notrunc bs=4096 seek=1

# Install platform tools
pushd platform
for file in *; do
	mcopy -i ../${FSBIN} ${file} ::
done
popd

mcopy -i ${FSBIN} config ::

mmd -i ${FSBIN} apps

for app in ${DEFAULT_APPS}; do
	mcopy -i ${FSBIN} apps/${app} ::apps/
done


# Create and push OTA update

TARGET=$1

PLATFORM_VER=$(cat platform/version.txt)
OTA_FN=badge-platform-ota-${PLATFORM_VER}.tar.gz

# https://git-scm.com/docs/git-archive
# need to remove pax_global_header
git archive --format=tgz HEAD^{tree} -o ${OTA_FN} platform
cat << __EOF__ > version.json
{
  "version": ${PLATFORM_VER},
  "ota_url": "https://badge.arcy.me/ota/${OTA_FN}"
}
__EOF__
scp version.json ${OTA_FN} $TARGET
rm version.json ${OTA_FN}
