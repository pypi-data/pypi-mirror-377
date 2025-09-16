from huggingface_hub import snapshot_download
import tensorflow as tf
import numpy as np
import pandas as pd

from monkeycall.helper import chunk_with_padding, load_audio_representation, z_norm, predictions_to_df


def load_model(
    architecture: str = "georgiosrizos/spider-monkey-dummy-detector",
    cache_dir: str | None = None  # TODO: To implement this.
):
    """
        Load a pre-trained spider monkey call detection model.

        Args:
            architecture: Model architecture name (e.g., "georgiosrizos/spider-monkey-dummy-detector").
            cache_dir: Local directory to cache downloaded weights.

        Returns:
            A tensorflow inference model.
        """

    if cache_dir is not None:
        raise NotImplementedError("Need to implement.")

    # This will create a local cache folder and return its path
    model_dir = snapshot_download(architecture)

    print(f"Model files downloaded to: {model_dir}")

    # Load the SavedModel with TensorFlow.
    model = tf.saved_model.load(model_dir)

    # Get the default inference function.
    inference_fn = model.signatures["serving_default"]

    return inference_fn


def predict_3_sec_clip(
    audio_path: str,
    model=None,
) -> dict | np.float32:
    """
    Run inference on an audio file.

    Args:
        audio_path: Path to WAV file.
        model: Preloaded model (optional). If None, loads default pretrained model.

    Returns:
        - prediction_probability: float the probability a whinny has been detected in this 3 sec clip.
    """
    logmel_spectrogram, custom_stats = load_audio_representation(audio_path)

    if logmel_spectrogram.shape[0] < 300:
        # Sample-scope z-norm
        logmel_spectrogram = z_norm(logmel_spectrogram, custom_stats)

        # Pad.
        logmel_spectrogram = np.pad(
            logmel_spectrogram,
            pad_width=((0, 300 - logmel_spectrogram.shape[0]), (0, 0)),  # (rows, cols)
            mode="constant",
            constant_values=0
        )
    elif logmel_spectrogram.shape[0] > 300:
        raise ValueError("This recording is more than 3 sec long. Please try the predict_recording() function instead.")
    else:
        pass

    outputs = model(tf.constant(logmel_spectrogram.reshape((1,
                                                            logmel_spectrogram.shape[0],
                                                            logmel_spectrogram.shape[1]))))["output"]

    outputs = tf.nn.sigmoid(outputs).numpy()  # Activate the logit to get prediction probability.

    return float(outputs[0, 0])


def predict_recording(
    audio_path: str,
    model=None,
    hop_size: int | None = 1,
    smoothing: str | None = None  # TODO: To implement this.
) -> dict | pd.DataFrame:
    """
        Run inference on an audio file.

        Args:
            audio_path: Path to WAV file.
            model: Preloaded model (optional). If None, loads default pretrained model.
            hop_size: Step size (in seconds) for windowing. Defaults to window_size.
            smoothing: Post-processing method ("peak", "median", etc.).

        Returns:
            - DataFrame with columns [timestamp_start, timestamp_end, prob_positive].
        """
    if smoothing is not None:
        raise NotImplementedError

    logmel_spectrogram, custom_stats = load_audio_representation(audio_path)

    # Pad or do windowing.
    if logmel_spectrogram.shape[0] <= 300:
        raise ValueError("This is a 3 sec long recording. Please try the predict_3_sec_clip() function instead.")
    else:
        # Windowing.
        window_size_frames = 300
        hop_size_frames = 100 * hop_size

        clip_list, custom_stats_list = chunk_with_padding(logmel_spectrogram, window=window_size_frames, hop=hop_size_frames)
        for i in range(len(clip_list)):
            clip_list[i] = z_norm(clip_list[i], custom_stats_list[i])

    output_list = list()
    for clip in clip_list:
        outputs = model(tf.constant(clip.reshape((1,
                                                  clip.shape[0],
                                                  clip.shape[1]))))["output"]

        outputs = tf.nn.sigmoid(outputs).numpy()  # Activate the logit to get prediction probability.
        output_list.append(float(outputs[0, 0]))

    data_frame = predictions_to_df(probs=output_list,
                                   clip_duration=3,
                                   hop=hop_size)

    return data_frame
