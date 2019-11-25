#!/usr/bin/env python
# -*- coding: utf-8 -*-




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
                                                   frame_formats[0].wWidth, frame_formats[0].wHeight,
                                                   int(1e7 / frame_formats[0].dwDefaultFrameInterval)
                                                   )

            with devi.stream() as s:
                try:
                    while True:
                        data = q.get(True, 500)
                        if data is None:
                            print("[*] DATA WAS NOONE [*]")
                            break
                        data = cv2.resize(data[:, :], (640, 480))
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
