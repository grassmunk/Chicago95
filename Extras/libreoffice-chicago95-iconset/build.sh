#!/bin/sh
# Startdate: 2021-03-26
# Goal: automate making the Chicago95 theme, for CI/CD.

TOPDIR="$( dirname "$( readlink -f "${0}" )" )" # for bgstack15, /mnt/public/work/vm2/icons/git
IMAGES_ZIP_SDIR="${TOPDIR}"/iconsets/c95
EXT_ZIP_SDIR="${TOPDIR}"/Chicago95-theme
OUTDIR="${TOPDIR}"

# PROCESS
rm -f "${OUTDIR}/images_chicago95.zip"
cd "${IMAGES_ZIP_SDIR}" ; 7za a "${OUTDIR}/images_chicago95.zip" *
mv -f "${OUTDIR}/images_chicago95.zip" "${EXT_ZIP_SDIR}/iconsets/"
rm -f "${OUTDIR}/Chicago95-theme-0.0.oxt"
cd "${EXT_ZIP_SDIR}" ; 7za a "${OUTDIR}/Chicago95-theme-0.0.oxt"
