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

import its.image
import its.device
import its.objects
import os.path
import numpy
import pylab
import matplotlib
import matplotlib.pyplot

def main():
    """Test 3A lock + YUV burst (using auto settings).

    This is a test that is designed to pass even on limited devices that
    don't have MANUAL_SENSOR or PER_FRAME_CONTROLS. (They must be able to
    capture bursts with full res @ full frame rate to pass, however).
    """
    NAME = os.path.basename(__file__).split(".")[0]

    BURST_LEN = 10
    SPREAD_THRESH = 0.005
    FPS_MAX_DIFF = 2.0

    with its.device.ItsSession() as cam:
        props = cam.get_camera_properties()

        # Converge 3A prior to capture.
        cam.do_3a(do_af=False, lock_ae=True, lock_awb=True)

        # After 3A has converged, lock AE+AWB for the duration of the test.
        req = its.objects.auto_capture_request()
        req["android.control.awbLock"] = True
        req["android.control.aeLock"] = True

        # Capture bursts of YUV shots.
        # Get the mean values of a center patch for each.
        r_means = []
        g_means = []
        b_means = []
        caps = cam.do_capture([req]*BURST_LEN)
        for i,cap in enumerate(caps):
            img = its.image.convert_capture_to_rgb_image(cap)
            its.image.write_image(img, "%s_frame%d.jpg"%(NAME,i))
            tile = its.image.get_image_patch(img, 0.45, 0.45, 0.1, 0.1)
            means = its.image.compute_image_means(tile)
            r_means.append(means[0])
            g_means.append(means[1])
            b_means.append(means[2])

        # Pass/fail based on center patch similarity.
        for means in [r_means, g_means, b_means]:
            spread = max(means) - min(means)
            print "Patch mean spread", spread
            assert(spread < SPREAD_THRESH)

        # Also ensure that the burst was at full frame rate.
        fmt_code = 0x23
        configs = props['android.scaler.streamConfigurationMap']\
                       ['availableStreamConfigurations']
        min_duration = None
        for cfg in configs:
            if cfg['format'] == fmt_code and cfg['input'] == False and \
                    cfg['width'] == caps[0]["width"] and \
                    cfg['height'] == caps[0]["height"]:
                min_duration = cfg["minFrameDuration"]
        assert(min_duration is not None)
        tstamps = [c['metadata']['android.sensor.timestamp'] for c in caps]
        deltas = [tstamps[i]-tstamps[i-1] for i in range(1,len(tstamps))]
        actual_fps = 1.0 / (max(deltas) / 1000000000.0)
        max_fps = 1.0 / (min_duration / 1000000000.0)
        print "FPS measured %.1f, max advertized %.1f" %(actual_fps, max_fps)
        assert(max_fps - FPS_MAX_DIFF <= actual_fps <= max_fps)

if __name__ == '__main__':
    main()

