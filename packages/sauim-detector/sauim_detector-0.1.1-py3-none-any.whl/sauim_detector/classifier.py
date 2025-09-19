import numpy as np
from tqdm import tqdm

def classify_signal(y, sr, model, clf):
    """
    Classify an audio signal into presence/absence of target events
    (e.g., tamarin vocalizations) using embeddings + OCSVM, 
    and merge overlapping windows into continuous detections.

    Steps:
    1. Slide a 5-second window across the signal with a hop of 1 second.
    2. Extract embeddings from the pre-trained model.
    3. Apply the OCSVM classifier to get a decision score.
    4. If score >= 0, mark as detection.
    5. Merge overlapping or consecutive detections:
       - If the new window starts inside the previous one → extend it.
       - Otherwise → open a new detection segment.

    Args:
        y (np.ndarray): input waveform
        sr (int): sampling rate
        model: embedding model with an `infer_tf` method
        clf: OCSVM classifier with `decision_function`

    Returns:
        list of tuples: [(start_time, end_time, label), ...]
    """
    detections = []
    prev_state = 0  # Previous frame state (0=no signal, 1=signal present)

    for i in tqdm(range(0, len(y) - 5*sr, sr)):
        frame = y[i:i+5*sr]

        # Feature extraction and classification
        model_outputs = model.infer_tf(frame[np.newaxis, :])
        decision_score = clf.decision_function(model_outputs['embedding'])
        current_state = 1 if decision_score >= 0.0 else 0

        if current_state == 1:
            start = i / sr
            end = (i + 5*sr) / sr

            if prev_state == 0:
                if detections and start <= detections[-1][1]:
                    # New window starts inside previous detection → extend it
                    detections[-1][1] = end
                else:
                    # Open a new detection
                    detections.append([start, end, "sauim"])
            else:
                # Extend the last detection
                detections[-1][1] = end

        prev_state = current_state

    # Convert inner lists to tuples for immutability
    return [tuple(d) for d in detections]
