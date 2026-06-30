#!/bin/sh
# Startdate: 2021-03-26
# Goal: automate making the Chicago95 theme, for CI/CD.

TOPDIR="$( dirname "$( readlink -f "${0}" )" )" # for bgstack15, /mnt/public/work/vm2/icons/git
EXT_ZIP_SDIR="${TOPDIR}"/Chicago95-theme
IMAGES_ZIP_SDIR="${EXT_ZIP_SDIR}"/iconsets/c95
OUTDIR="${TOPDIR}"

# PROCESS
rm -f "${EXT_ZIP_SDIR}/iconsets/images_chicago95.zip"
cd "${IMAGES_ZIP_SDIR}" ; 7za a "${EXT_ZIP_SDIR}/iconsets/images_chicago95.zip" *
rm -f "${OUTDIR}/Chicago95-theme-0.0.oxt"
cd "${EXT_ZIP_SDIR}" ; 7za a "${OUTDIR}/Chicago95-theme-0.0.oxt"
