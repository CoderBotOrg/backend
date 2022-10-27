#!/bin/bash
CUR_DIR=$(pwd)
cd /coderbot
wget -nc https://github.com/CoderBotOrg/net-models/raw/master/archive/cnn_models.tar.xz
tar xJf cnn_models.tar.xz
rm cnn_models.tar.xz
echo '{"generic_fast_low":{"status":1.0, "image_height": "128", "image_width":"128", "output_layer": "MobilenetV2/Predictions/Reshape_1"}, "generic_slow_high":{"status":1.0, "image_height":"224", "image_width": "224", "output_layer": "MobilenetV2/Predictions/Reshape_1"}}' > models.json
cd $CUR_DIR