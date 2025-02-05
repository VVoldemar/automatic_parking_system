# import RPi.GPIO as GPIO
# from time import sleep

# direction_pin = 24
# pulse_pin = 23
# delay = 500 * 1e-6

# GPIO.setmode(GPIO.BCM)

# GPIO.setup(direction_pin, GPIO.OUT)
# GPIO.setup(pulse_pin, GPIO.OUT)

# direction = True

# while True:
#     # GPIO.output(pulse_pin, GPIO.HIGH)
#     # sleep(0.3)
#     # GPIO.output(pulse_pin, GPIO.LOW)
#     # sleep(0.3)
#     if direction:
#         GPIO.output(direction_pin, GPIO.HIGH)
#     else:
#         GPIO.output(direction_pin, GPIO.LOW)
    
#     direction = not direction

#     for _ in range(50):
#         GPIO.output(pulse_pin, GPIO.HIGH)
#         sleep(delay)
#         GPIO.output(pulse_pin, GPIO.LOW)
#         sleep(delay)
#     sleep(1)

#!/usr/bin/env python3

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (C) 2022, Tomi Valkeinen <tomi.valkeinen@ideasonboard.com>

# A simple capture example extending the simple-capture.py example:
# - Capture frames using events from multiple cameras
# - Listening events from stdin to exit the application
# - Memory mapping the frames and calculating CRC

import binascii
import libcamera as libcam
import selectors
import sys

class MappedFrameBuffer:
    """
    Provides memoryviews for the FrameBuffer's planes
    """
    def __init__(self, fb: libcam.FrameBuffer):
        self.__fb = fb
        self.__planes = ()
        self.__maps = ()

    def __enter__(self):
        return self.mmap()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.munmap()

    def mmap(self):
        if self.__planes:
            raise RuntimeError('MappedFrameBuffer already mmapped')

        import os
        import mmap

        fb = self.__fb

        # Collect information about the buffers

        bufinfos = {}

        for plane in fb.planes:
            fd = plane.fd

            if fd not in bufinfos:
                buflen = os.lseek(fd, 0, os.SEEK_END)
                bufinfos[fd] = {'maplen': 0, 'buflen': buflen}
            else:
                buflen = bufinfos[fd]['buflen']

            if plane.offset > buflen or plane.offset + plane.length > buflen:
                raise RuntimeError(f'plane is out of buffer: buffer length={buflen}, ' +
                                   f'plane offset={plane.offset}, plane length={plane.length}')

            bufinfos[fd]['maplen'] = max(bufinfos[fd]['maplen'], plane.offset + plane.length)

        # mmap the buffers

        maps = []

        for fd, info in bufinfos.items():
            map = mmap.mmap(fd, info['maplen'], mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
            info['map'] = map
            maps.append(map)

        self.__maps = tuple(maps)

        # Create memoryviews for the planes

        planes = []

        for plane in fb.planes:
            fd = plane.fd
            info = bufinfos[fd]

            mv = memoryview(info['map'])

            start = plane.offset
            end = plane.offset + plane.length

            mv = mv[start:end]

            planes.append(mv)

        self.__planes = tuple(planes)

        return self

    def munmap(self):
        if not self.__planes:
            raise RuntimeError('MappedFrameBuffer not mmapped')

        for p in self.__planes:
            p.release()

        for mm in self.__maps:
            mm.close()

        self.__planes = ()
        self.__maps = ()

    @property
    def planes(self) -> tuple[memoryview, ...]:
        """memoryviews for the planes"""
        if not self.__planes:
            raise RuntimeError('MappedFrameBuffer not mmapped')

        return self.__planes

    @property
    def fb(self):
        return self.__fb

# A container class for our state per camera
class CameraCaptureContext:
    idx: int
    cam: libcam.Camera
    reqs: list[libcam.Request]
    mfbs: dict[libcam.FrameBuffer, MappedFrameBuffer]

    def __init__(self, cam, idx):
        self.idx = idx
        self.cam = cam

        # Acquire the camera for our use

        cam.acquire()

        # Configure the camera

        cam_config = cam.generate_configuration([libcam.StreamRole.Viewfinder])

        stream_config = cam_config.at(0)

        cam.configure(cam_config)

        stream = stream_config.stream

        # Allocate the buffers for capture

        allocator = libcam.FrameBufferAllocator(cam)
        ret = allocator.allocate(stream)
        assert ret > 0

        num_bufs = len(allocator.buffers(stream))

        print(f'cam{idx} ({cam.id}): capturing {num_bufs} buffers with {stream_config}')

        # Create the requests and assign a buffer for each request

        self.reqs = []
        self.mfbs = {}

        for i in range(num_bufs):
            # Use the buffer index as the "cookie"
            req = cam.create_request(idx)

            buffer = allocator.buffers(stream)[i]
            req.add_buffer(stream, buffer)

            self.reqs.append(req)

            # Save a mmapped buffer so we can calculate the CRC later
            self.mfbs[buffer] = MappedFrameBuffer(buffer).mmap()

    def uninit_camera(self):
        # Stop the camera

        self.cam.stop()

        # Release the camera

        self.cam.release()


# A container class for our state
class CaptureContext:
    cm: libcam.CameraManager
    camera_contexts: list[CameraCaptureContext] = []

    def handle_camera_event(self):
        # cm.get_ready_requests() returns the ready requests, which in our case
        # should almost always return a single Request, but in some cases there
        # could be multiple or none.

        reqs = self.cm.get_ready_requests()

        # Process the captured frames

        for req in reqs:
            self.handle_request(req)

        return True

    def handle_request(self, req: libcam.Request):
        cam_ctx = self.camera_contexts[req.cookie]

        buffers = req.buffers

        assert len(buffers) == 1

        # A ready Request could contain multiple buffers if multiple streams
        # were being used. Here we know we only have a single stream,
        # and we use next(iter()) to get the first and only buffer.

        stream, fb = next(iter(buffers.items()))

        # Use the MappedFrameBuffer to access the pixel data with CPU. We calculate
        # the crc for each plane.

        mfb = cam_ctx.mfbs[fb]
        crcs = [binascii.crc32(p) for p in mfb.planes]

        

        meta = fb.metadata

        print('cam{:<6} seq {:<6} bytes {:10} CRCs {}'
              .format(cam_ctx.idx,
                      meta.sequence,
                      '/'.join([str(p.bytes_used) for p in meta.planes]),
                      crcs))

        # We want to re-queue the buffer we just handled. Instead of creating
        # a new Request, we re-use the old one. We need to call req.reuse()
        # to re-initialize the Request before queuing.

        req.reuse()
        cam_ctx.cam.queue_request(req)

    def handle_key_event(self):
        sys.stdin.readline()
        print('Exiting...')
        return False

    def capture(self):
        # Queue the requests to the camera

        for cam_ctx in self.camera_contexts:
            for req in cam_ctx.reqs:
                cam_ctx.cam.queue_request(req)

        # Use Selector to wait for events from the camera and from the keyboard

        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ, self.handle_key_event)
        sel.register(self.cm.event_fd, selectors.EVENT_READ, lambda: self.handle_camera_event())

        running = True

        while running:
            events = sel.select()
            for key, mask in events:
                # If the handler return False, we should exit
                if not key.data():
                    running = False

def camera_name(camera):
    props = camera.properties
    location = props.get(libcam.properties.Location, None)

    if location == libcam.properties.LocationEnum.Front:
        name = 'Internal front camera'
    elif location == libcam.properties.LocationEnum.Back:
        name = 'Internal back camera'
    elif location == libcam.properties.LocationEnum.External:
        name = 'External camera'
        if libcam.properties.Model in props:
            name += f' "{props[libcam.properties.Model]}"'
    else:
        name = 'Undefined location'

    name += f' ({camera.id})'

    return name

def main():
    cm = libcam.CameraManager.singleton()

    for camera in cm.cameras:
        print(camera_name(camera))

    if len(cm.cameras) == 0:
        print("No cameras found")

    ctx = CaptureContext()
    ctx.cm = cm

    for idx, cam in enumerate(cm.cameras):
        cam_ctx = CameraCaptureContext(cam, idx)
        ctx.camera_contexts.append(cam_ctx)

    # Start the cameras

    for cam_ctx in ctx.camera_contexts:
        cam_ctx.cam.start()

    ctx.capture()

    for cam_ctx in ctx.camera_contexts:
        cam_ctx.uninit_camera()

    return 0


if __name__ == '__main__':
    sys.exit(main())
