import collections
import time
import threading
import numpy as np
from typing import List, Optional
from ctypes import *
from enum import Enum
import sys

from imswitch.imcommon.model import initLogger

# Platform-specific imports
if sys.platform.startswith('linux'):
    try:
        from imswitch.imcontrol.model.interfaces.tucam.TUCam import *
        TUCSEN_SDK_AVAILABLE = True
        TUCSEN_PLATFORM = "linux"
    except Exception as e:
        print(f"Could not import Tucsen camera libraries for Linux: {e}")
        TUCSEN_SDK_AVAILABLE = False
        TUCSEN_PLATFORM = None
elif sys.platform.startswith('win'):
    try:
        from imswitch.imcontrol.model.interfaces.tucam_win.TUCam import *
        TUCSEN_SDK_AVAILABLE = True
        TUCSEN_PLATFORM = "windows"
    except Exception as e:
        print(f"Could not import Tucsen camera libraries for Windows: {e}")
        TUCSEN_SDK_AVAILABLE = False
        TUCSEN_PLATFORM = None
else:
    print(f"Tucsen camera interface not supported on {sys.platform}")
    TUCSEN_SDK_AVAILABLE = False
    TUCSEN_PLATFORM = None

class TucsenMode(Enum):
    HDR = 0
    CMS = 1
    HIGH_SPEED = 2


class CameraTucsen:
    """Threaded continuous-grab Tucsen wrapper compatible with ImSwitch."""

    @staticmethod
    def force_cleanup():
        try:
            if TUCSEN_PLATFORM == "windows":
                TUCAM_Api_Uninit()
                time.sleep(0.2)
        except Exception as e:
            print(f"Force cleanup warning: {e}")

    @staticmethod
    def _rc(ret) -> int:
        try:
            return int(ret.value) if hasattr(ret, "value") else int(ret)
        except Exception:
            return 0

    @staticmethod
    def _ok(ret) -> bool:
        try:
            success = TUCAMRET.TUCAMRET_SUCCESS.value
        except Exception:
            success = 0
        return CameraTucsen._rc(ret) == success

    def __init__(self, cameraNo=None, exposure_time=10000, gain=0, frame_rate=-1, blacklevel=100, isRGB=False, binning=1):
        super().__init__()
        self.__logger = initLogger(self, tryInheritParent=False)

        self.model = "CameraTucsen"
        self.shape = (0, 0)
        self.is_connected = False

        self.blacklevel = blacklevel
        self.exposure_time = exposure_time
        self.gain = gain
        self.frame_rate = frame_rate
        self.cameraNo = cameraNo if cameraNo is not None else 0
        self.isRGB = bool(isRGB)
        self.binning = binning

        self.NBuffer = 5
        self.frame_buffer = collections.deque(maxlen=self.NBuffer)
        self.frameid_buffer = collections.deque(maxlen=self.NBuffer)

        self.SensorHeight = 0
        self.SensorWidth = 0

        self.lastFrameFromBuffer = None
        self.lastFrameId = -1
        self.frameNumber = -1

        # Threading
        self._read_thread_lock = threading.Lock()
        self._read_thread: Optional[threading.Thread] = None
        self._keep_running = threading.Event()
        self._is_streaming = threading.Event()
        self._frame_lock = threading.Lock()

        self._current_frame: Optional[np.ndarray] = None
        self._m_frame: Optional["TUCAM_FRAME"] = None
        self.camera_handle = None

        if not TUCSEN_SDK_AVAILABLE:
            raise Exception("Tucsen SDK not available")

        if TUCSEN_PLATFORM == "windows":
            self.Path = './'
            self.TUCAMINIT = None
            self.TUCAMOPEN = None

        self._open_camera(self.cameraNo)
        self.trigger_source = "Continuous"
        self.isFlatfielding = False
        self.flatfieldImage = None

    # -------- Open/close ----------------------------------------------------
    def _open_camera(self, camera_index: int):
        try:
            if TUCSEN_PLATFORM == "linux":
                self._open_camera_linux(camera_index)
            elif TUCSEN_PLATFORM == "windows":
                self._open_camera_windows(camera_index)
            else:
                raise Exception("Unsupported platform for Tucsen camera")
        except Exception as e:
            self.__logger.error(f"Failed to open Tucsen camera: {e}")
            self.is_connected = False
            raise

    def _open_camera_linux(self, camera_index: int):
        ret = TUCAM_Api_Init()
        # Do not hard-fail on non-zero here; Linux bindings may return 0/None
        opCam = TUCAM_OPEN()
        opCam.uiIdxOpen = camera_index
        ret = TUCAM_Dev_Open(byref(opCam))
        if not self._ok(ret):
            raise Exception(f"Failed to open Tucsen camera {camera_index}: {ret}")
        self.camera_handle = opCam.hIdxTUCam
        self._get_sensor_info()
        self.is_connected = True
        self.__logger.info(f"Opened Tucsen camera {camera_index} (Linux)")

    def _open_camera_windows(self, camera_index: int):
        try:
            TUCAM_Api_Uninit()
            time.sleep(0.1)
        except Exception:
            pass
        self.TUCAMINIT = TUCAM_INIT(0, self.Path.encode('utf-8'))
        self.TUCAMOPEN = TUCAM_OPEN(0, 0)
        ret = TUCAM_Api_Init(pointer(self.TUCAMINIT), 5000)
        self.__logger.info(f"API Init result: {ret}")
        if self.TUCAMINIT.uiCamCount == 0:
            raise Exception("No Tucsen cameras found")
        if camera_index >= self.TUCAMINIT.uiCamCount:
            raise Exception(f"Camera index {camera_index} not available. Found {self.TUCAMINIT.uiCamCount} cameras")
        self.TUCAMOPEN = TUCAM_OPEN(camera_index, 0)
        TUCAM_Dev_Open(pointer(self.TUCAMOPEN))
        if self.TUCAMOPEN.hIdxTUCam == 0:
            raise Exception(f"Failed to open Tucsen camera {camera_index}")
        self.camera_handle = self.TUCAMOPEN.hIdxTUCam
        self._get_sensor_info()
        self.is_connected = True
        self.__logger.info(f"Opened Tucsen camera {camera_index} (Windows)")

    def _get_sensor_info(self):
        try:
            temp = TUCAM_FRAME()
            temp.pBuffer = 0
            temp.ucFormatGet = TUFRM_FORMATS.TUFRM_FMT_USUAl.value
            temp.uiRsdSize = 1
            ret = TUCAM_Buf_Alloc(self.camera_handle, pointer(temp))
            if self._ok(ret):
                self.SensorWidth = int(temp.usWidth)
                self.SensorHeight = int(temp.usHeight)
                TUCAM_Buf_Release(self.camera_handle)
            else:
                self.SensorWidth = 2048
                self.SensorHeight = 2048
        except Exception as e:
            self.__logger.warning(f"Sensor info fallback: {e}")
            self.SensorWidth = 2048
            self.SensorHeight = 2048
        self.shape = (self.SensorHeight, self.SensorWidth)

    def openPropertiesGUI(self): 
        """Open camera properties GUI (placeholder)."""
        self.__logger.info("Properties GUI not implemented for Tucsen camera")

    def setPropertyValue(self, property_name, property_value):
        """Unified setter used by TucsenCamManager."""
        try:
            key = str(property_name).strip().lower().replace(" ", "_")
            if key in ("exposure", "exposure_time"):
                self.set_exposure_time(float(property_value))
                return self.exposure_time
            elif key == "gain":
                self.set_gain(float(property_value))
                return self.gain
            elif key == "blacklevel":
                self.set_blacklevel(float(property_value))
                return self.blacklevel
            elif key == "binning":
                self.setBinning(int(property_value))
                return self.binning
            elif key == "frame_rate":
                self.frame_rate = float(property_value)
                return self.frame_rate
            elif key in ("trigger_source", "trigger"):
                self.setTriggerSource(str(property_value))
                return self.trigger_source
            elif key in ("image_width", "width"):
                # read-only; return current
                return int(self.SensorWidth)
            elif key in ("image_height", "height"):
                # read-only; return current
                return int(self.SensorHeight)
            elif key in ("flat_fielding", "flatfielding"):
                self.isFlatfielding = bool(property_value)
                return self.isFlatfielding
            else:
                self.__logger.warning(f"Unknown property '{property_name}'")
                return self.getPropertyValue(property_name)
        except Exception as e:
            self.__logger.error(f"setPropertyValue('{property_name}', {property_value}) failed: {e}")
            return None


    def getPropertyValue(self, property_name):
        """Unified getter used by TucsenCamManager."""
        try:
            key = str(property_name).strip().lower().replace(" ", "_")
            if key in ("exposure", "exposure_time"):
                return self.exposure_time
            elif key == "gain":
                return self.gain
            elif key == "blacklevel":
                return self.blacklevel
            elif key == "binning":
                return self.binning
            elif key == "frame_rate":
                return self.frame_rate
            elif key in ("trigger_source", "trigger"):
                return self.trigger_source
            elif key in ("image_width", "width"):
                return int(self.SensorWidth)
            elif key in ("image_height", "height"):
                return int(self.SensorHeight)
            elif key == "model":
                return self.model
            elif key in ("isrgb",):
                return bool(self.isRGB)
            elif key in ("flat_fielding", "flatfielding"):
                return bool(self.isFlatfielding)
            else:
                self.__logger.warning(f"Unknown property '{property_name}'")
                return None
        except Exception as e:
            self.__logger.error(f"getPropertyValue('{property_name}') failed: {e}")
            return None

    # -------- Live control (threaded) ---------------------------------------
    def start_live(self):
        if self._is_streaming.is_set():
            self.__logger.warning("Camera is already streaming")
            return
        # Clear buffers
        self.flushBuffer()
        # Allocate frame
        self._allocate_buffer()
        # Set properties
        self.set_exposure_time(self.exposure_time)
        self.set_gain(self.gain)
        self.set_blacklevel(self.blacklevel)
        # Start capture
        ret = TUCAM_Cap_Start(self.camera_handle, TUCAM_CAPTURE_MODES.TUCCM_SEQUENCE.value)
        if not self._ok(ret):
            try:
                if self._m_frame is not None:
                    TUCAM_Buf_Release(self.camera_handle)
                    self._m_frame = None
            finally:
                raise Exception(f"Failed to start capture: {ret}")
        # Thread
        with self._read_thread_lock:
            self._keep_running.set()
            self._is_streaming.set()
            self._read_thread = threading.Thread(target=self._wait_for_frame, name="TucsenRead", daemon=True)
            self._read_thread.start()
        self.__logger.info("Tucsen streaming started")

    def stop_live(self):
        if not self._is_streaming.is_set():
            self.__logger.warning("Camera is not streaming")
            return
        # Unblock WaitForFrame BEFORE join
        try:
            TUCAM_Buf_AbortWait(self.camera_handle)
        except Exception:
            pass
        with self._read_thread_lock:
            self._keep_running.clear()
            thread = self._read_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=3.0)
        # Stop & release
        try:
            ret = TUCAM_Cap_Stop(self.camera_handle)
            if not self._ok(ret):
                self.__logger.warning(f"Cap_Stop returned {ret}")
        except Exception as e:
            self.__logger.warning(f"Cap_Stop error: {e}")
        try:
            if self._m_frame is not None:
                TUCAM_Buf_Release(self.camera_handle)
        except Exception as e:
            self.__logger.warning(f"Buf_Release error: {e}")
        self._m_frame = None
        self._read_thread = None
        self._is_streaming.clear()
        self.__logger.info("Tucsen streaming stopped")

    suspend_live = stop_live

    def _allocate_buffer(self):
        self._m_frame = TUCAM_FRAME()
        self._m_frame.pBuffer = 0
        self._m_frame.ucFormatGet = TUFRM_FORMATS.TUFRM_FMT_USUAl.value
        self._m_frame.uiRsdSize = 1
        ret = TUCAM_Buf_Alloc(self.camera_handle, pointer(self._m_frame))
        self.__logger.info(f"Buf_Alloc -> {ret}")
        if not self._ok(ret):
            self._m_frame = None
            raise Exception(f"Failed to allocate buffer: {ret}")

    def _wait_for_frame(self):
        consecutive_timeouts = 0
        max_timeouts = 10
        while self._keep_running.is_set():
            try:
                # Wait up to 1000 ms; Tucsen Python wrapper often raises on timeout
                TUCAM_Buf_WaitForFrame(self.camera_handle, pointer(self._m_frame), 1000)
                consecutive_timeouts = 0
                frame_np = self._convert_frame_to_numpy(self._m_frame)
                if frame_np is not None:
                    with self._frame_lock:
                        self.frameNumber += 1
                        self.frame_buffer.append(frame_np)
                        self.frameid_buffer.append(self.frameNumber)
                        self._current_frame = frame_np
                # small yield to avoid burning CPU
                time.sleep(0.001)
            except Exception as ex:
                s = str(ex)
                if "TIMEOUT" in s or "-2147483128" in s:
                    consecutive_timeouts += 1
                    if consecutive_timeouts >= max_timeouts:
                        self.__logger.warning("Consecutive timeouts; camera may be idle")
                        consecutive_timeouts = 0
                else:
                    self.__logger.warning(f"WaitForFrame error: {ex}")
                time.sleep(0.001)

    # -------- Frame conversion ----------------------------------------------
    def _convert_frame_to_numpy(self, frame: "TUCAM_FRAME") -> Optional[np.ndarray]:
        try:
            if frame.uiImgSize == 0 or frame.pBuffer == 0:
                return None
            buf = create_string_buffer(frame.uiImgSize)
            pointer_data = c_void_p(frame.pBuffer + frame.usHeader)
            memmove(buf, pointer_data, frame.uiImgSize)
            data = bytes(buf)
            if frame.ucElemBytes == 1:
                dtype = np.uint8
            elif frame.ucElemBytes == 2:
                dtype = np.uint16
            else:
                self.__logger.warning(f"Unsupported elem size: {frame.ucElemBytes}")
                return None
            arr = np.frombuffer(data, dtype=dtype)
            if frame.ucChannels == 1:
                arr = arr.reshape((int(frame.usHeight), int(frame.usWidth)))
            elif frame.ucChannels == 3:
                arr = arr.reshape((int(frame.usHeight), int(frame.usWidth), 3))
            else:
                self.__logger.warning(f"Unsupported channels: {frame.ucChannels}")
                return None
            # Flatfield (optional)
            if self.isFlatfielding and self.flatfieldImage is not None:
                try:
                    arr = arr.astype(np.float32)
                    arr = arr - self.flatfieldImage
                except Exception:
                    pass
            return arr
        except Exception as e:
            self.__logger.error(f"Convert frame failed: {e}")
            return None

    # -------- Parameters & properties ---------------------------------------
    def get_camera_parameters(self):
        return {
            "model": self.model,
            "isRGB": self.isRGB,
            "width": self.SensorWidth,
            "height": self.SensorHeight,
            "exposure_time": self.exposure_time,
            "gain": self.gain,
            "blacklevel": self.blacklevel,
            "binning": self.binning,
        }

    def get_gain(self):
        try:
            return (self.gain, 0.0, 100.0)
        except Exception as e:
            self.__logger.error(f"Failed to get gain: {e}")
            return (None, None, None)

    def get_exposuretime(self):
        try:
            return (self.exposure_time, 0.1, 10000.0)
        except Exception as e:
            self.__logger.error(f"Failed to get exposure time: {e}")
            return (None, None, None)

    def set_exposure_time(self, exposure_time):
        try:
            self.exposure_time = exposure_time
            exposure_us = float(exposure_time) * 1000.0
            ret = TUCAM_Prop_SetValue(self.camera_handle, TUCAM_IDPROP.TUIDP_EXPOSURETM.value, c_double(exposure_us), 0)
            if not self._ok(ret):
                self.__logger.warning(f"Set exposure returned {ret}")
        except Exception as e:
            self.__logger.error(f"Failed to set exposure time: {e}")

    def set_gain(self, gain):
        try:
            self.gain = gain
            ret = TUCAM_Prop_SetValue(self.camera_handle, TUCAM_IDPROP.TUIDP_GLOBALGAIN.value, c_double(float(gain)), 0)
            if not self._ok(ret):
                self.__logger.warning(f"Set gain returned {ret}")
        except Exception as e:
            self.__logger.error(f"Failed to set gain: {e}")

    def set_blacklevel(self, blacklevel):
        try:
            self.blacklevel = blacklevel
            ret = TUCAM_Prop_SetValue(self.camera_handle, TUCAM_IDPROP.TUIDP_BLACKLEVEL.value, c_double(float(blacklevel)), 0)
            if not self._ok(ret):
                self.__logger.warning(f"Set blacklevel returned {ret}")
        except Exception as e:
            self.__logger.error(f"Failed to set blacklevel: {e}")

    def setBinning(self, binning=1):
        try:
            self.binning = binning
            # TODO: apply via Tucsen API if available for your model
        except Exception as e:
            self.__logger.error(f"Failed to set binning: {e}")

    # -------- Buffer & retrieval --------------------------------------------
    def getLast(self, returnFrameNumber: bool = False, timeout: float = 1.0, auto_trigger: bool = True):
        t0 = time.time()
        while not self.frame_buffer:
            if time.time() - t0 > timeout:
                return (None, None) if returnFrameNumber else None
            time.sleep(0.001)
        with self._frame_lock:
            frame = self.frame_buffer[-1] if self.frame_buffer else None
            frame_id = self.frameid_buffer[-1] if self.frameid_buffer else -1
        return (frame, frame_id) if returnFrameNumber else frame

    def flushBuffer(self):
        with self._frame_lock:
            self.frameid_buffer.clear()
            self.frame_buffer.clear()

    def getLastChunk(self):
        with self._frame_lock:
            frames = list(self.frame_buffer)
            ids = list(self.frameid_buffer)
            self.flushBuffer()
        self.lastFrameFromBuffer = frames[-1] if frames else None
        return frames, ids

    # -------- Triggering -----------------------------------------------------
    def getTriggerTypes(self) -> List[str]:
        return ["Continuous", "Software Trigger", "External Trigger"]

    def getTriggerSource(self) -> str:
        return self.trigger_source

    def setTriggerSource(self, trigger_source):
        try:
            self.trigger_source = trigger_source
            ts = trigger_source.strip().lower()
            if ts in ("continuous", "continous", "free run"):
                val = 0
            elif ts in ("software", "software trigger"):
                val = 1
            elif ts in ("external", "external trigger"):
                val = 2
            else:
                val = 0
            try:
                TUCAM_Capa_SetValue(self.camera_handle, TUCAM_IDCAPA.TUIDC_TRIGGERMODES.value, val)
            except Exception:
                pass
        except Exception as e:
            self.__logger.error(f"Failed to set trigger source: {e}")

    def send_trigger(self):
        try:
            ret = TUCAM_Cap_DoSoftwareTrigger(self.camera_handle)
            return self._ok(ret)
        except Exception as e:
            self.__logger.error(f"Failed to send trigger: {e}")
            return False

    # -------- Flatfield stubs ------------------------------------------------
    def setFlatfieldImage(self, flatfieldImage, isFlatfielding):
        self.flatfieldImage = flatfieldImage
        self.isFlatfielding = bool(isFlatfielding)

    def recordFlatfieldImage(self, n=16, median=False):
        if not self._is_streaming.is_set():
            return
        frames = []
        t_end = time.time() + 2.0  # simple time cap
        while len(frames) < n and time.time() < t_end:
            f = self.getLast(timeout=0.2)
            if f is not None:
                frames.append(f.astype(np.float32))
        if frames:
            stack = np.stack(frames, axis=0)
            self.flatfieldImage = (np.median(stack, axis=0) if median else np.mean(stack, axis=0)).astype(np.float32)
            self.isFlatfielding = True

    # -------- Close ----------------------------------------------------------
    def close(self):
        try:
            if self._is_streaming.is_set():
                self.stop_live()
            if TUCSEN_PLATFORM == "linux":
                self._close_camera_linux()
            elif TUCSEN_PLATFORM == "windows":
                self._close_camera_windows()
        except Exception as e:
            self.__logger.error(f"Failed to close camera: {e}")

    def _close_camera_linux(self):
        if self.camera_handle:
            ret = TUCAM_Dev_Close(self.camera_handle)
            if not self._ok(ret):
                self.__logger.warning(f"Dev_Close returned {ret}")
        try:
            TUCAM_Api_Uninit()
        except Exception:
            pass
        self.is_connected = False
        self.__logger.info("Camera closed (Linux)")

    def _close_camera_windows(self):
        try:
            try:
                TUCAM_Buf_AbortWait(self.camera_handle)
            except Exception:
                pass
            try:
                TUCAM_Cap_Stop(self.camera_handle)
            except Exception:
                pass
            try:
                if self._m_frame is not None:
                    TUCAM_Buf_Release(self.camera_handle)
            except Exception:
                pass
            if self.camera_handle and self.camera_handle != 0:
                try:
                    ret = TUCAM_Dev_Close(self.camera_handle)
                    if not self._ok(ret):
                        self.__logger.warning(f"Dev_Close returned {ret}")
                except Exception as e:
                    self.__logger.warning(f"Error closing device: {e}")
            time.sleep(0.1)
            try:
                TUCAM_Api_Uninit()
            except Exception:
                pass
        finally:
            self.camera_handle = None
            self.is_connected = False
            self.__logger.info("Camera closed (Windows)")

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

