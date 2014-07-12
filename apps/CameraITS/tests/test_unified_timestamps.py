# Copyright 2014 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import its.device
import its.objects
import os.path
import time

def main():
    """Test if image and motion sensor events are in the same time domain.
    """
    NAME = os.path.basename(__file__).split(".")[0]

    with its.device.ItsSession() as cam:

        # TODO: Get camera props and skip test if capability not claimed.

        # Get the timestamp of a captured image.
        req = its.objects.auto_capture_request()
        cap = cam.do_capture(req)
        ts_image0 = cap['metadata']['android.sensor.timestamp']

        # Get the timestamps of motion events.
        cam.start_sensor_events()
        time.sleep(1)
        events = cam.get_sensor_events()
        assert(len(events["gyro"]) > 0)
        assert(len(events["accel"]) > 0)
        assert(len(events["mag"]) > 0)
        ts_gyro0 = events["gyro"][0]["time"]
        ts_gyro1 = events["gyro"][-1]["time"]
        ts_accel0 = events["accel"][0]["time"]
        ts_accel1 = events["accel"][-1]["time"]
        ts_mag0 = events["mag"][0]["time"]
        ts_mag1 = events["mag"][-1]["time"]

        # Get the timestamp of another iamge.
        req = its.objects.auto_capture_request()
        cap = cam.do_capture(req)
        ts_image1 = cap['metadata']['android.sensor.timestamp']

        print "Image timestamps:", ts_image0, ts_image1
        print "Gyro timestamps:", ts_gyro0, ts_gyro1
        print "Accel timestamps:", ts_accel0, ts_accel1
        print "Mag timestamps:", ts_mag0, ts_mag1

        # The motion timestamps must be between the two image timestamps.
        assert ts_image0 < min(ts_gyro0, ts_accel0, ts_mag0) < ts_image1
        assert ts_image0 < max(ts_gyro1, ts_accel1, ts_mag1) < ts_image1

if __name__ == '__main__':
    main()
