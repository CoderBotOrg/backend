#!/bin/bash
CUR_DIR=$(pwd)
cd /usr/lib/arm-linux-gnueabihf
ln -s libbcm_host.so.0 libbcm_host.so
ln -s libmmal.so.0 libmmal.so
ln -s libmmal_core.so.0 libmmal_core.so
ln -s libmmal_util.so.0 libmmal_util.so
ln -s libmmal_vc_client.so.0 libmmal_vc_client.so
ln -s libbcm_host.so.0 libbcm_host.so
ln -s libvcsm.so.0 libvcsm.so
ln -s libvchiq_arm.so.0 libvchiq_arm.so
ln -s libvcos.so.0 libvcos.so
cd $CUR_DIR