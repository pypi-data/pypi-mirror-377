import ctypes
import ctypes.util
import os
import sys
from importlib import resources

import numpy as np
import numpy.typing as npt


class RNNoise:
    """
    RNNoise Python bindings for noise reduction

    Supports 1ch 48000Hz int16 ndarray
    """

    def __init__(
        self, library_path: str | None = None, model_path: str | None = None
    ) -> None:
        """
        Initialize RNNoise

        Args:
            library_path: Path to librnnoise.so
            model_path: Path to custom model file (optional)
        """
        if library_path is None:
            library_path = self.__find_rnnoise_library()
        self.__lib: ctypes.CDLL = ctypes.CDLL(library_path)
        self.__setup_function_signatures()
        self.__model: ctypes.c_void_p | None = None
        if model_path and os.path.exists(model_path):
            self.__model = self.__lib.rnnoise_model_from_filename(
                ctypes.c_char_p(model_path.encode("utf-8"))
            )
        self.__state: ctypes.c_void_p = self.__lib.rnnoise_create(self.__model)
        if not self.__state:
            raise RuntimeError("Failed to create RNNoise state")
        self.__frame_size: int = self.__lib.rnnoise_get_frame_size()

    def __find_rnnoise_library(self) -> str:
        """Find path librnnoise.so"""
        # 環境変数で指定されたライブラリを参照
        env_lib: str | None = os.environ.get("RNNOISE_LIB_PATH")
        if env_lib and os.path.exists(env_lib):
            return env_lib

        # パッケージ内のライブラリを参照
        package_lib: str | None = self.__find_package_rnnoise_library()
        if package_lib and os.path.exists(package_lib):
            return package_lib

        # システムのライブラリを参照
        system_lib: str | None = ctypes.util.find_library("rnnoise")
        if system_lib:
            return system_lib
        raise FileNotFoundError("librnnoise is not found. Set RNNOISE_LIB_PATH.")

    def __find_package_rnnoise_library(self) -> str | None:
        if sys.platform.startswith("linux"):
            libname = "librnnoise.so"
        else:
            return None
        return str(resources.files("rnnoisepy").joinpath("lib", libname))

    def __setup_function_signatures(self) -> None:
        """Setup ctypes function signatures"""
        # rnnoise_get_size
        self.__lib.rnnoise_get_size.restype = ctypes.c_int
        self.__lib.rnnoise_get_size.argtypes = []

        # rnnoise_get_frame_size
        self.__lib.rnnoise_get_frame_size.restype = ctypes.c_int
        self.__lib.rnnoise_get_frame_size.argtypes = []

        # rnnoise_create
        self.__lib.rnnoise_create.restype = ctypes.c_void_p
        self.__lib.rnnoise_create.argtypes = [ctypes.c_void_p]

        # rnnoise_destroy
        self.__lib.rnnoise_destroy.restype = None
        self.__lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]

        # rnnoise_process_frame
        self.__lib.rnnoise_process_frame.restype = ctypes.c_float
        self.__lib.rnnoise_process_frame.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]

        # rnnoise_model_from_filename
        self.__lib.rnnoise_model_from_filename.restype = ctypes.c_void_p
        self.__lib.rnnoise_model_from_filename.argtypes = [ctypes.c_char_p]

        # rnnoise_model_free
        self.__lib.rnnoise_model_free.restype = None
        self.__lib.rnnoise_model_free.argtypes = [ctypes.c_void_p]

    @property
    def frame_size(self) -> int:
        """Get RNNoise frame size"""
        return self.__frame_size

    def __int16_to_float(
        self, audio_data: npt.NDArray[np.int16]
    ) -> npt.NDArray[np.float32]:
        """Convert int16 audio to float32 (direct conversion)"""
        return audio_data.astype(np.float32)

    def __float_to_int16(
        self, audio_data: npt.NDArray[np.float32]
    ) -> npt.NDArray[np.int16]:
        """Convert float32 audio to int16 (direct conversion)"""
        return audio_data.astype(np.int16)

    def process_frame(
        self, audio_frame: npt.NDArray[np.int16]
    ) -> tuple[npt.NDArray[np.int16], float]:
        """
        Process a single frame of audio

        Args:
            audio_frame: int16(le) 48000Hz mono audio frame of size frame_size

        Returns:
            tuple: (denoised_frame, voice_probability (0.0 - 1.0))
        """
        if len(audio_frame) != self.__frame_size:
            raise ValueError(
                f"Frame size must be {self.__frame_size}, got {len(audio_frame)}"
            )

        x: npt.NDArray[np.float32] = self.__int16_to_float(audio_frame)

        # Create ctypes pointer (in-place processing)
        x_ptr: ctypes._Pointer[ctypes.c_float] = x.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        )

        # Process frame - RNNoise uses in-place processing (same buffer for input and output)
        voice_prob: float = float(
            self.__lib.rnnoise_process_frame(self.__state, x_ptr, x_ptr)
        )

        # Convert back to int16 (direct conversion)
        output_int16: npt.NDArray[np.int16] = self.__float_to_int16(x)

        return output_int16, voice_prob

    def __del__(self) -> None:
        if hasattr(self, "_RNNoise__state") and self.__state:
            self.__lib.rnnoise_destroy(self.__state)

        if hasattr(self, "_RNNoise__model") and self.__model:
            self.__lib.rnnoise_model_free(self.__model)
