############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################

import time
import os
import math
import json
import logging
import pathlib
from PIL import Image as PILImage
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

from cv import camera, image, blob

from cnn.cnn_manager import CNNManager

import config

MAX_IMAGE_AGE = 0.0
PHOTO_PATH = "data/media"
PHOTO_METADATA_FILE = "data/media/metadata.json"
PHOTO_PREFIX = "DSC"
VIDEO_PREFIX = "VID"
PHOTO_THUMB_SUFFIX = "_thumb"
PHOTO_THUMB_SIZE = (240, 180)
VIDEO_ELAPSE_MAX = 900

class Camera(object):

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Camera()
            #cls._instance.start()
        return cls._instance

    def __init__(self):
        logging.info("starting camera")
        cam_props = {"width":640, "height":512,
                     "cv_image_factor": config.Config.get().get("cv_image_factor"),
                     "exposure_mode": config.Config.get().get("camera_exposure_mode"),
                     "framerate": config.Config.get().get("camera_framerate"),
                     "bitrate": config.Config.get().get("camera_jpeg_bitrate"),
                     "jpeg_quality": int(config.Config.get().get("camera_jpeg_quality"))}
        self._camera = camera.Camera(props=cam_props)
        self.recording = False
        self.video_start_time = time.time() + 8640000
        self._image_time = 0
        self._cv_image_factor = int(config.Config.get().get("cv_image_factor", 4))
        self._image_refresh_timeout = float(config.Config.get().get("camera_refresh_timeout", 0.1))
        self._color_object_size_min = int(config.Config.get().get("camera_color_object_size_min", 80)) / (self._cv_image_factor * self._cv_image_factor)
        self._color_object_size_max = int(config.Config.get().get("camera_color_object_size_max", 32000)) / (self._cv_image_factor * self._cv_image_factor)
        self._path_object_size_min = int(config.Config.get().get("camera_path_object_size_min", 80)) / (self._cv_image_factor * self._cv_image_factor)
        self._path_object_size_max = int(config.Config.get().get("camera_path_object_size_max", 32000)) / (self._cv_image_factor * self._cv_image_factor)
        self.load_photo_metadata()
        if not self._photos:
            self._photos = []
            for filenames in os.walk(PHOTO_PATH):
                for filename in filenames[2]:
                    if (PHOTO_PREFIX in filename or VIDEO_PREFIX in filename) and PHOTO_THUMB_SUFFIX not in filename:
                        self._photos.append({'name': filename})
            self.save_photo_metadata()

        self._cnn_classifiers = {}
        cnn_model = config.Config.get().get("cnn_default_model", "")
        if cnn_model != "":
            try:
                self._cnn_classifiers[cnn_model] = CNNManager.get_instance().load_model(cnn_model)
                self._cnn_classifier_default = self._cnn_classifiers[cnn_model]
                logging.info("loaded: " + cnn_model + " " + str(self._cnn_classifier_default))
            except Exception:
                logging.warning("model not found: %s", cnn_model)

        self._camera.grab_start()
        self._image_cv = self.get_image()

        super(Camera, self).__init__()

    def get_image(self):
        return image.Image(self._camera.get_image_bgr())

    def get_image_cv_jpeg(self):
        return self._image_cv.to_jpeg()

    def set_image_cv(self, an_image):
        self._image_cv = an_image

    def get_image_jpeg(self):
        return self._camera.get_image_jpeg()

    def set_text(self, text):
        self._camera.set_overlay_text(str(text))

    def load_photo_metadata(self):
        try:
            with open(PHOTO_METADATA_FILE, "rt") as f:
                self._photos = json.load(f)
                f.close()
        except Exception:
            logging.warning("no metadata file, starting from empty")
            pathlib.Path(PHOTO_PATH).mkdir(parents=True, exist_ok=True)
            self._photos = []
            self.save_photo_metadata()

    def save_photo_metadata(self):
        f = open(PHOTO_METADATA_FILE, "wt")
        json.dump(self._photos, f)
        f.close()

    def update_photo(self, photo):
        for p in self._photos:
            if p["name"] == photo["name"]:
                p["tag"] = photo["tag"]
        self.save_photo_metadata()

    def get_next_photo_index(self):
        last_photo_index = 0
        for p in self._photos:
            try:
                index = int(p["name"][len(PHOTO_PREFIX):-len(self._camera.PHOTO_FILE_EXT)])
                if index > last_photo_index:
                    last_photo_index = index
            except Exception:
                pass
        return last_photo_index + 1

    def photo_take(self):
        photo_index = self.get_next_photo_index()
        filename = PHOTO_PREFIX + str(photo_index) + self._camera.PHOTO_FILE_EXT
        filename_thumb = PHOTO_PREFIX + str(photo_index) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT
        of = open(PHOTO_PATH + "/" + filename, "wb+")
        oft = open(PHOTO_PATH + "/" + filename_thumb, "wb+")
        im_str = self.get_image_jpeg()
        of.write(im_str)
        # thumb
        im_pil = PILImage.open(BytesIO(im_str))
        im_pil.resize(PHOTO_THUMB_SIZE).save(oft)
        self._photos.append({"name":filename})
        self.save_photo_metadata()
        of.close()
        oft.close()

    def is_recording(self):
        return self.recording

    def video_rec(self, video_name=None):
        if self.is_recording():
            return
        self.recording = True

        if video_name is None:
            video_index = self.get_next_photo_index()
            filename = VIDEO_PREFIX + str(video_index) + self._camera.VIDEO_FILE_EXT
            filename_thumb = VIDEO_PREFIX + str(video_index) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT
        else:
            filename = VIDEO_PREFIX + video_name + self._camera.VIDEO_FILE_EXT
            filename_thumb = VIDEO_PREFIX + video_name + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT
            try:
                #remove previous file and reference in album
                os.remove(PHOTO_PATH + "/" + filename)
                self._photos.remove({"name":filename})
            except Exception:
                pass

        oft = open(PHOTO_PATH +  "/" + filename_thumb, "wb")
        im_str = self._camera.get_image_jpeg()
        im_pil = PILImage.open(BytesIO(im_str))
        im_pil.resize(PHOTO_THUMB_SIZE).save(oft)
        self._photos.append({"name":filename})
        self.save_photo_metadata()
        self._camera.video_rec(PHOTO_PATH + "/" + filename)
        self.video_start_time = time.time()
        oft.close()

    def video_stop(self):
        if self.recording:
            self._camera.video_stop()
            self.recording = False

    def get_photo_list(self):
        return self._photos

    def get_photo_file(self, filename):
        return open(PHOTO_PATH + "/" + filename, "rb")

    def get_photo_thumb_file(self, filename):
        return open(PHOTO_PATH + "/" + filename[:-len(self._camera.PHOTO_FILE_EXT)] + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT, "rb")

    def delete_photo(self, filename):
        logging.info("delete photo: %s", filename)
        os.remove(PHOTO_PATH + "/" + filename)
        os.remove(PHOTO_PATH + "/" + filename[:filename.rfind(".")] + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT)
        for photo in self._photos:
            if photo["name"] == filename:
                self._photos.remove(photo)
        self.save_photo_metadata()

    def exit(self):
        #self.join()
        self.video_stop()
        self._camera.grab_stop()

    def get_average(self):
        avg = self.get_image().get_average()
        return avg

    def find_line(self):
        img = self.get_image()
        avg = img.get_average()
        img = img.binarize(int((avg[0]+avg[2])/2))
        img = img.erode().dilate()
        if int(img._data.mean()) > 127:
            img = img.invert()
        slices = [0, 0, 0]
        blobs = [0, 0, 0]
        slices[0] = img.crop(0, int(self._camera.out_rgb_resolution[1]/1.2), self._camera.out_rgb_resolution[0], self._camera.out_rgb_resolution[1])
        slices[1] = img.crop(0, int(self._camera.out_rgb_resolution[1]/1.5), self._camera.out_rgb_resolution[0], int(self._camera.out_rgb_resolution[1]/1.2))
        slices[2] = img.crop(0, int(self._camera.out_rgb_resolution[1]/2.0), self._camera.out_rgb_resolution[0], int(self._camera.out_rgb_resolution[1]/1.5))
        y_offset = [int(self._camera.out_rgb_resolution[1]/1.2),
                    int(self._camera.out_rgb_resolution[1]/1.5),
                    int(self._camera.out_rgb_resolution[1]/2.0)]
        coords = [-1, -1, -1]
        for idx, slc in enumerate(slices):
            blobs[idx] = slc.find_blobs(minsize=2000/(self._cv_image_factor * self._cv_image_factor), maxsize=16000/(self._cv_image_factor * self._cv_image_factor))
            if blobs[idx]:
                coords[idx] = (blobs[idx][0].center[0] * 100) / self._camera.out_rgb_resolution[0]
                blb = blobs[idx][0]
                img.draw_rect(blb.left, y_offset[idx] + blb.top, blb.right, y_offset[idx] + blb.bottom, (0, 255, 0), 5)
        self.set_image_cv(img)
        return coords

    def find_face(self):
        face_x = face_y = face_size = None
        img = self.get_image()
        faces = img.grayscale().find_faces()
        if len(faces):
            # Get the largest face, face is a rectangle
            x, y, w, h = faces[0]
            center_x = x + (w/2)
            face_x = ((center_x * 100) / self._camera.out_rgb_resolution[0]) - 50 #center = 0
            center_y = y + (h/2)
            face_y = 50 - (center_y * 100) / self._camera.out_rgb_resolution[1] #center = 0
            size = h
            face_size = (size * 100) / self._camera.out_rgb_resolution[1]
            logging.info("face found, x: " + str(face_x) + " y: " + str(face_y) + " size: " + str(face_size))
        return [face_x, face_y, face_size]

    def path_ahead(self):
        image_size = self._camera.out_rgb_resolution
        img = self.get_image()

        size_y = img._data.shape[0]
        size_x = img._data.shape[1]
        threshold = img.crop(0, size_y - int(size_y/12), size_x, size_y)._data.mean() / 2

        blobs = img.binarize(threshold).dilate().find_blobs(minsize=self._path_object_size_min, maxsize=self._path_object_size_max)
        coordY = 60
        if blobs:
            obstacle = blob.Blob.sort_distance((image_size[0]/2, image_size[1]), blobs)[0]

            coords = img.transform([(obstacle.center[0], obstacle.bottom)], img.get_transform(img.size()[1]))
            x = coords[0][0]
            y = coords[0][1]
            coordY = 60 - ((y * 48) / (480 / self._cv_image_factor))
            logging.info("x: %s y: %s coordY: %s", str(x), str(y), str(coordY))

        return coordY

    def find_color(self, s_color):
        image_size = self._camera.out_rgb_resolution
        color = (int(s_color[1:3], 16), int(s_color[3:5], 16), int(s_color[5:7], 16))
        #ts = time.time()
        img = self.get_image()
        bw = img.filter_color(color)
        objects = bw.find_blobs(minsize=self._color_object_size_min, maxsize=self._color_object_size_max)
        logging.debug("objects: %s", str(objects))
        dist = -1
        angle = 180
        fov_offset = 12 #cm
        fov_total_y = 68 #cm
        fov_total_x = 60 #cm

        if objects:
            obj = objects[-1]
            logging.info("bottom: " + str(obj.center[0]) + " " + str(obj.bottom))
            coords = bw.transform([(obj.center[0], obj.bottom)], bw.get_transform(bw.size()[1]))
            logging.info("coordinates: %s", str(coords))
            x = coords[0][0]
            y = coords[0][1]
            dist = math.sqrt(math.pow(fov_offset + (fov_total_y * (image_size[1] - y) / (image_size[1]/1.2)), 2) + (math.pow((x-(image_size[0]/2)) * fov_total_x / image_size[0], 2)))
            angle = math.atan2(x - (image_size[0]/2), image_size[1] - y) * 180 / math.pi
            logging.info("object found, dist: " + str(dist) + " angle: " + str(angle))
        #self.save_image(img.to_jpeg())
        #print "object: " + str(time.time() - ts)
        return [dist, angle]

    def find_text(self, lang="en", timeout=0):
        t1 = time.time()
        text = None
        #color = (int(back_color[1:3], 16), int(back_color[3:5], 16), int(back_color[5:7], 16))
        img = self.get_image()
        #rec_image = img.find_rect(color=color)
        text = img.find_text(lang, timeout)
        logging.info("find_text fps: " + str(1.0/(time.time() - t1)))
        #if rec_image:
        #    logging.info("image: %s", str(rec_image))
        #    bin_image = rec_image.binarize().invert()
        #    text = bin_image.find_text(accept)
        return text

    def find_qr_code(self):
        img = self.get_image()
        return img.find_qr_code()

    def find_ar_code(self):
        img = self.get_image()
        return img.find_ar_code()

    def cnn_classify(self, model_name=None, top_results=3):
        classifier = None
        if model_name:
            classifier = self._cnn_classifiers.get(model_name)
            if classifier is None:
                classifier = CNNManager.get_instance().load_model(model_name)
                self._cnn_classifiers[model_name] = classifier
        else:
            classifier = self._cnn_classifier_default

        t0 = time.time()
        classes = None
        try:
            img = self.get_image()
            classes = classifier.classify_image(img.mat(), top_results=top_results)
        except Exception:
            logging.warning("classifier not available")
            classes = [("None", 1.0)]
            raise
        logging.info("fps: %f", 1.0/(time.time()-t0))
        return classes

    def find_class(self):
        return self.cnn_classify(top_results=1)[0][0]

    def cnn_detect_objects(self, model_name=None, top_results=3):
        classifier = None
        if model_name:
            classifier = self._cnn_classifiers.get(model_name)
            if classifier is None:
                classifier = CNNManager.get_instance().load_model(model_name)
                self._cnn_classifiers[model_name] = classifier
        else:
            classifier = self._cnn_classifier_default

        t0 = time.time()
        classes = None
        try:
            img = self.get_image()
            classes = classifier.detect_objects(img.mat(), top_results=top_results)
        except Exception:
            logging.warning("classifier not available")
            classes = [("None", 100)]
            raise
        logging.info("fps: %f", 1.0/(time.time()-t0))
        return classes
