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

from time import time
import logging
import numpy as np
import cv2
from cv import image

from coderbot import CoderBot
from camera import Camera
from config import Config

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict(maxCorners=500,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)


PI_CAM_FOV_H_DEG = 53.0
PI_CAM_FOV_V_CM = 100.0

class Motion:
    # pylint: disable=too-many-instance-attributes

    def __init__(self, settings):
        self.bot = CoderBot.get_instance(settings)
        self.cam = Camera.get_instance(settings)
        self.track_len = 2
        self.detect_interval = 5
        self.tracks = []
        self.frame_idx = 0
        self.ts = time()
        self.frame_gray = None
        self.prev_gray = None
        self.running = False
        self.delta_power = 0.0
        self.delta_dist = 0.0
        self.target_dist = 0.0
        self.delta_angle = 0.0
        self.target_angle = 0.0
        self.power_angles = [[15, (int(settings.get("move_power_angle_1")), -1)],
                             [4, (int(settings.get("move_power_angle_2")), 0.05)],
                             [1, (int(settings.get("move_power_angle_3")), 0.02)],
                             [0, (0, 0)]]
        self.image_width = 640 / int(settings.get("cv_image_factor"))
        self.image_heigth = 480 / int(settings.get("cv_image_factor"))
        self.transform = image.Image.get_transform(self.image_width)
    _motion = None

    @classmethod
    def get_instance(cls, settings=None):
        if not cls._motion:
            cls._motion = Motion(settings)
        return cls._motion

    def move(self, dist):
        self.delta_dist = 0.0
        self.delta_angle = 0.0
        self.target_dist = dist
        self.target_angle = 0.0
        self.delta_power = 0.0
        self.loop_move()

    def turn(self, angle):
        self.delta_dist = 0.0
        self.delta_angle = 0.0
        self.target_dist = 0.0
        self.target_angle = angle
        self.loop_turn()

    def stop(self):
        self.running = False

    def loop_move(self):
        self.running = True
        while self.running:
            frame = self.cam.get_image()
            self.frame_gray = frame.grayscale()

            if len(self.tracks) < 2 or self.frame_idx % self.detect_interval == 0:
                self.find_keypoints(self.frame_gray, self.tracks)

            if self.tracks and self.prev_gray is not None:
                self.track_keypoints(self.prev_gray, self.frame_gray, self.tracks)

            if self.tracks:
                delta_angle, delta_dist = self.calc_motion()
                self.running = self.running and self.bot_move(self.target_dist, delta_dist, delta_angle)

            self.frame_idx += 1
            self.prev_gray = self.frame_gray
        self.bot.stop()

    def loop_turn(self):
        self.running = True
        while self.running:
            frame = self.cam.get_image()
            self.frame_gray = frame.grayscale()

            if len(self.tracks) < 2 or self.frame_idx % self.detect_interval == 0:
                self.find_keypoints(self.frame_gray, self.tracks)

            if self.tracks and self.prev_gray is not None:
                self.track_keypoints(self.prev_gray, self.frame_gray, self.tracks)

            if self.tracks:
                delta_angle, delta_dist = self.calc_motion()
                self.running = self.running and self.bot_turn(self.target_angle, delta_angle)

            self.frame_idx += 1
            self.prev_gray = self.frame_gray

        self.bot.stop()

    def find_keypoints(self, image_gray, tracks):
        #print "find_keypoints"
        ts = time()
        mask = np.zeros_like(image_gray._data)
        mask[:] = 255
        #for x, y in [np.int32(tr[-1]) for tr in tracks]:
        #    cv2.circle(mask, (x, y), 5, 0, -1)
        p = cv2.goodFeaturesToTrack(image_gray._data, mask=mask, **feature_params)
        if p is not None:
            for x, y in np.float32(p).reshape(-1, 2):
                tracks.append([(x, y)])
        #print "fk: ", str(time() - ts)

    def track_keypoints(self, prev_image, cur_image, tracks):
        #print "track_keypoints"
        #ts = time()
        img0, img1 = prev_image._data, cur_image._data
        p0 = np.float32([tr[-1] for tr in tracks]).reshape(-1, 1, 2)
        p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
        p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
        d = abs(p0-p0r).reshape(-1, 2).max(-1)
        good = d < 1
        #good = st
        #print "tk: ", str(time() - ts)
        new_tracks = []
        for tr, (x, y), good_flag in zip(tracks, p1.reshape(-1, 2), good):
            if not good_flag:
                continue
            tr.append((x, y))
            if len(tr) > self.track_len:
                del tr[0]
            new_tracks.append(tr)
            #cv2.circle(self.vis, (x, y), 2, (0, 255, 0), -1)
        #print "initial tp: ", len(self.tracks), " current tp: ", len(new_tracks)
        #print len(new_tracks), len(tracks)
        tracks[:] = new_tracks[:]
        if tracks is False:
            logging.warning("lost ALL tp!")
            self.bot.stop()
            #exit(0)
        #cv2.polylines(self.vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))

    def calc_motion(self):
        vectors = self.tracks

        avg_delta_x = 0.0
        avg_delta_y = 0.0
        count = 0
        vectors_t = []
        for vect in vectors:
            if len(vect) > 1:
                count += 1
                vectors_t.append(vect[-2])
                vectors_t.append(vect[-1])
                avg_delta_x += (vect[-1][0] - vect[-2][0])

        vectors_t = vectors_t[:min(len(vectors_t), 20)] #max 10 keypoints

        #avg_delta_x_t = 0.0
        if vectors_t:
            vectors_t = image.Image.transform(vectors_t, self.transform)
            for v in vectors_t.reshape(-1, 2, 2):
                avg_delta_y += (v[1][1] - v[0][1])
                #avg_delta_x_t += v[1][0] - v[0][0]
            #avg_delta_x_t = avg_delta_x_t / (vectors_t.shape[0] / 2)
            #for v in vectors_t.reshape(-1, 2, 2):
                #if abs(v[1][0] - v[0][0] - avg_delta_x_t) > 2:
                    #print "this is an obstacle: ", str(v[1]), " delta_x: ", v[1][0] - v[0][0]

        if count > 0:
            avg_delta_x = (avg_delta_x / count)
            avg_delta_y = (avg_delta_y / (vectors_t.shape[0] / 2))

            self.delta_angle -= (avg_delta_x * PI_CAM_FOV_H_DEG) / self.image_width
            self.delta_dist += (avg_delta_y * PI_CAM_FOV_V_CM) / self.image_heigth
            #print "count: ", count, "delta_a: ", self.delta_angle, " avg_delta_x: ", avg_delta_x, " delta_y: ", self.delta_dist, " avg_delta_y: ", avg_delta_y

        #cv2.line(self.vis, (int(80+deltaAngle),20), (80,20), (0, 0, 255))
        #cv2.putText(self.vis, "delta: " + str(int((self.deltaAngle*53.0)/160.0)) + " avg_delta: " + str(int(((avg_delta_x*53.0)/160.0))),
                     #(0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255))

        return self.delta_angle, self.delta_dist

    def bot_turn(self, target_angle, delta_angle):
        run = True
        sign = (target_angle - delta_angle) / abs(target_angle - delta_angle)
        logging.info("abs delta: %s sign delta: %s", str(abs(target_angle - delta_angle)), str(sign))
        for p_a in self.power_angles:
            if abs(target_angle - delta_angle) > p_a[0] and self.running:
                #print "pow: ", p_a[1][0], " duration: ", p_a[1][1]
                self.bot.motor_control(sign * p_a[1][0], -1 * sign * p_a[1][0], p_a[1][1])
                run = p_a[1][0] > 0 #stopped
                break

        return run

    def bot_move(self, target_dist, delta_dist, delta_angle):
        base_power = 100 * (target_dist/abs(target_dist))
        self.delta_power += (delta_angle * 0.01)
        logging.info("base power: %s delta power: %s delta_dist: %s target_dist: %s", str(base_power), str(self.delta_power), str(delta_dist), str(target_dist))
        if abs(delta_dist) < abs(target_dist):
            self.bot.motor_control(min(max(base_power - self.delta_power, -100), 100), min(max(base_power + self.delta_power, -100), 100), -1)
        else:
            self.bot.stop()
        return abs(delta_dist) < abs(target_dist)
