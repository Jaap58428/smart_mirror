#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uvctypes import *
import time
import cv2
import numpy as np
try:
  from queue import Queue
except ImportError:
  from Queue import Queue
import platform

BUF_SIZE = 10
q = Queue(BUF_SIZE)

def py_frame_callback(frame, userptr):

  array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
  data = np.frombuffer(
    array_pointer.contents, dtype=np.dtype(np.uint16)
  ).reshape(
    frame.contents.height, frame.contents.width
  ) # no copy

  # data = np.fromiter(
  #   frame.contents.data, dtype=np.dtype(np.uint8), count=frame.contents.data_bytes
  # ).reshape(
  #   frame.contents.height, frame.contents.width, 2
  # ) # copy

  if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
    return

  if not q.full():
    q.put(data)

PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def ktof(val):
  return (1.8 * ktoc(val) + 32.0)

def ktoc(val):
  return (val - 27315) / 100.0

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def display_temperature(img, val_k, loc, color):
  val = ktof(val_k)
  cv2.putText(img,"{0:.1f} degF".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
  x, y = loc
  cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
  cv2.line(img, (x, y - 2), (x, y + 2), color, 1)

class Context():
    def __init__(self):
        self.ctx = POINTER(uvc_context)()
        self.dev = POINTER(uvc_device)()
        self.handle = POINTER(uvc_device_handle)()
        self.ctrl = uvc_stream_ctrl()
    
    def uvc(self):    
        return Uvc(self)

class UvcInitError(Exception):
    pass


class DeviceNotFound(Exception):
    pass


class DeviceNotAvailable(Exception):
    pass


class StreamError(Exception):
    pass


class Uvc():
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        res = libuvc.uvc_init(byref(self.context.ctx), 0)
        if res < 0:
            raise UvcInitError("Failed to initialize UVC")
        
        return self

    def __exit__(self, *args):
        libuvc.uvc_exit(self.context.ctx)
    
    def find_device(self):
        res = libuvc.uvc_find_device(self.context.ctx, byref(self.context.dev), PT_USB_VID, PT_USB_PID, 0)
        if res < 0:
            raise DeviceNotFound("Could not find UVC device")
        
        return

    def open(self):
        self.find_device()
        return Device(self.context)


class Device():
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        res = libuvc.uvc_open(self.context.dev, byref(self.context.handle))
        if res < 0:
            raise DeviceNotAvailable("Failed to open device")
        
        return self

    def __exit__(self, *args):
        libuvc.uvc_unref_device(self.context.dev)
    
    def device_info(self):
        print_device_info(self.context.handle)
    
    def device_formats(self):
        print_device_formats(self.context.handle)

    def stream(self):
        return Stream(self.context)


class Stream():
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        res = libuvc.uvc_start_streaming(self.context.handle, byref(self.context.ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
        if res < 0:
            raise StreamError("Failed to start stream")
        
        return self
    
    def __exit__(self, *args):
        libuvc.uvc_stop_streaming(self.context.handle)


def main():
    ctx = Context()
    
    with ctx.uvc() as uvc:
        with uvc.open() as devi:
            
            devi.device_info()
            devi.device_formats()

            frame_formats = uvc_get_frame_formats_by_guid(devi.context.handle, VS_FMT_GUID_Y16)
            if len(frame_formats) == 0:
                print("device does not support Y16")
                exit(1)

            libuvc.uvc_get_stream_ctrl_format_size(devi.context.handle, byref(devi.context.ctrl), UVC_FRAME_FORMAT_Y16,
                frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
            )

            with devi.stream() as s:
                try:
                    while True:
                        data = q.get(True, 500)
                        if data is None:
                            print("[*] DATA WAS NOONE [*]")
                            break
                        data = cv2.resize(data[:,:], (640, 480))
                        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
                        img = raw_to_8bit(data)
                        display_temperature(img, minVal, minLoc, (255, 0, 0))
                        display_temperature(img, maxVal, maxLoc, (0, 0, 255))
                        cv2.imshow('Lepton Radiometry', img)
                        cv2.waitKey(1)
                    cv2.destroyAllWindows()
                except Exception as e:
                    print("[*] EXCEPTION OCCURED [*]")
                    print(e)
if __name__ == '__main__':
  main()
