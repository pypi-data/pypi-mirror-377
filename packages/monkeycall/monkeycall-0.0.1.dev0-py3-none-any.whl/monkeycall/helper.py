import librosa
import numpy as np
import pandas as pd


def load_audio_representation(audio_path: str):
    """
        Loads audio clip, resamples to required sampling rate, extracts required mel spectrograms.

        Args:
            audio_path: str of filepath of audio file.

        Returns:
            logmel_spectrogram: np.array of dtype np.float32.
            custom_stats: dict containing statistics (mean, std, max_abs) of the recording.
        """
    waveform, _ = librosa.load(audio_path, sr=16000)

    logmel_spectrogram,  \
    custom_stats = get_features_and_stats(waveform)

    return logmel_spectrogram.astype(np.float32), custom_stats


def get_features_and_stats(waveform):
    """
        Extracts logmel spectrogram from audio waveform, and calculates some stats of the clip.

        Args:
            waveform: np.array of the audio signal waveform.

        Returns:
            logmel_spectrogram: np.array of dtype np.float32.
            custom_stats: dict containing statistics (mean, std, max_abs) of the recording.
    """
    spectrogram = np.abs(librosa.stft(waveform, n_fft=2048, hop_length=10 * 16)) ** 1.0
    logmel_spectrogram = librosa.power_to_db(
        librosa.feature.melspectrogram(y=waveform, sr=16000, S=spectrogram))

    logmel_spectrogram = logmel_spectrogram.transpose()[:-1, :]

    custom_stats = dict()
    custom_stats["mean"] = np.mean(logmel_spectrogram, axis=0)
    custom_stats["std"] = np.std(logmel_spectrogram, axis=0)
    custom_stats["max_abs"] = np.max(np.abs(logmel_spectrogram))

    return logmel_spectrogram, custom_stats


def chunk_with_padding(logmel_spectrogram: np.ndarray,
                       window: int = 300,
                       hop: int = 300) -> list[np.ndarray]:
    """
        Split `logmel_spectrogram` (N, F) into overlapping or non-overlapping chunks of shape (window, F).
        The final chunk is zero-padded if it has fewer than `window` rows.

        Args:
            logmel_spectrogram: np.array of the log mel spectrogram of the audio signal.
            window: int -- the number of log mel spectrogram time frames in the window; default corresponds to 3 sec.
            hop: int -- the number of log mel spectrogram time frames to hop; default corresponds to 3 sec.

        Returns:
            chunks: list of 3 sec corresponding log mel spectrograms of dtype np.float32.
            custom_stats: list containing statistics (mean, std, max_abs) of the corresponding chunk log mel spectrogram.

    """
    n_frames, n_features = logmel_spectrogram.shape
    chunks = []
    custom_stats_list = []

    for start in range(0, n_frames, hop):
        end = start + window
        slice_ = logmel_spectrogram[start:end]

        custom_stats = dict()
        custom_stats["mean"] = np.mean(slice_, axis=0)
        custom_stats["std"] = np.std(slice_, axis=0)
        custom_stats["max_abs"] = np.max(np.abs(slice_))

        if slice_.shape[0] < window:
            # pad rows at the end
            pad_rows = window - slice_.shape[0]
            slice_ = np.pad(
                slice_,
                pad_width=((0, pad_rows), (0, 0)),
                mode="constant",
                constant_values=0
            )
        chunks.append(slice_)
        custom_stats_list.append(custom_stats)

        if end >= n_frames:
            break  # we reached the end

    return chunks, custom_stats_list


def z_norm(logmel_spectrogram, custom_stats):
    """
        Applies z-normalisation to a log mel spectrogram.

        Args:
            logmel_spectrogram: np.array of the log mel spectrogram of the audio signal.
            custom_stats: dict containing statistics (mean, std, max_abs) of the recording.

        Returns:
            logmel_spectrogram: np.array of dtype np.float32.
            window: int -- the number of log mel spectrogram time frames in the window; default corresponds to 3 sec.
            hop: int -- the number of log mel spectrogram time frames to hop; default corresponds to 3 sec.
    """
    std = custom_stats["std"]
    std[std == 0.0] = 1.0
    logmel_spectrogram = (logmel_spectrogram - custom_stats["mean"]) / std
    return logmel_spectrogram


def predictions_to_df(probs, clip_duration: float, hop: float = None) -> pd.DataFrame:
    """
        Create a DataFrame with start_time, end_time, probability for each clip prediction.

        Args:
            probs: list or np.ndarray of probabilities
            clip_duration: seconds per clip
            hop: hop size in seconds between clip starts. Defaults to clip_duration (non-overlapping).

        Returns:
            df: pd.DataFrame containing windowed clip start-end times and corresponding detection probability.

    """
    # TODO: The max recording length might not be divisible by 3 sec.
    probs = np.asarray(probs)
    if hop is None:
        hop = clip_duration

    starts = np.arange(len(probs)) * hop
    ends   = starts + clip_duration

    df = pd.DataFrame({
        "start_time": starts,
        "end_time": ends,
        "probability": probs
    })
    return df
