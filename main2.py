from uvctypes import *
from contextlib import contextmanager
from queue import Queue
import platform
import numpy as np
import cv2

BUF_SIZE = 2
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

class UvcInitError(Exception):
    pass


class UvcFindDeviceError(Exception):
    pass


class UvcDeviceOpenError(Exception):
    pass


class Y16NotSupportedError(Exception):
    pass


class StartStreamError(Exception):
    pass


'''
Tries to init uvc with the given arguments.
Throws a UvcInitError if it fails.
'''
def raw_uvc_init(uvc_ctx, usb_ctx):
    res = libuvc.uvc_init(uvc_ctx, usb_ctx)

    if res < 0:
        raise UvcInitError("Failed to init raw_uvc_init")

'''
Tries to init uvc with the given arguments.
This can be used as `with uvc_init(args) as _:`
to automatically cleanup the uvc resource.
'''
@contextmanager
def uvc_init(uvc_ctx, usb_ctx):
    raw_uvc_init(uvc_ctx, usb_ctx)

    try:
        yield
    finally:
        libuvc.uvc_exit(uvc_ctx)

def raw_uvc_find_device(uvc_ctx, dev, *args):
    # https://ken.tossell.net/libuvc/doc/group__device.html#ga03a47cf340e03fafdca15cfc35620922
    res = libuvc.find_device(uvc_ctx, dev, *args)

    if res < 0:
        raise UvcFindDeviceError("Failed to find uvc device")

@contextmanager
def find_uvc_device(uvc_ctx, dev, *args):
    raw_uvc_find_device(uvc_ctx, dev, *args)

    try:
        yield
    finally:
        pass

def raw_uvc_open(dev, devh):
    res = libuvc.uvc_open(dev, devh)

    if res < 0:
        raise UvcDeviceOpenError("Failed to open uvc device")

@contextmanager
def uvc_open(dev, devh):
    raw_uvc_open(dev, devh)

    try:
        yield
    finally:
        libuvc.uvc_unref_device(dev)

def raw_uvc_start_streaming(devh, ctrl, *args):
    res = libuvc.uvc_start_streaming(devh, ctrl, *args)

    if res < 0:
        raise StartStreamError("Couldn't start uvc stream: {}".format(res))

@contextmanager
def start_streaming(devh, ctrl, *args):
    raw_uvc_start_streaming(devh, ctrl, *args)

    try:
        yield
    finally:
        libuvc.stop_streaming(devh)

def uvc_get_frame_formats_by_guid_wrapper(devh, *args):
    frame_formats = uvc_get_frame_formats_by_guid(devh, *args)

    if len(frame_formats) == 0:
        raise Y16NotSupportedError("Y16 is not supported by this device")

    return frame_formats

def streaming(callme_maybe):
    ctx = POINTER(uvc_context)()
    dev = POINTER(uvc_device)()
    devh = POINTER(uvc_device_handle)()
    ctrl = uvc_stream_ctrl()

    with uvc_init(byref(ctx), 0):
        with find_uvc_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0):
            with uvc_open(dev, byref(devh)):
                print_device_info(devh)
                print_device_formats(devh)

                frame_formats = uvc_get_frame_formats_by_guid_wrapper(devh, VS_FMT_GUID_Y16)

                libuvc.uvc_stream_ctrl_format_size(
                    devh, byref(ctrl), UVC_FRAME_FORMAT_Y16, frame_formats[0].wWidth,
                    frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
                )

                with start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0):
                    while True:
                        data = q.get(True, 500)
                        if data is None:
                            continue
                        callme_maybe(data)

                    cv2.destroyAllWindows()

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def showimg(data):
    data = cv2.resize(data[:,:], (640, 480))
    img = raw_to_8bit(data)
    cv2.imshow('Lepton Radiometry', img)
    cv2.waitKey(1)

if __name__ == '__main__':
    streaming(showimg)