# 🐒 Sauim Detector

`sauim-detector` is a Python command-line tool for **bioacoustic processing** and **automatic detection of Pied tamarin (Saguinus bicolor) vocalizations**. It combines a pre-trained **bird vocalization embedding model** with a custom **OCSVM classifier** to detect the presence of tamarin calls in audio recordings. 🙈🙉🙊

---

## 📦 Installation

Clone and install the package:

```bash
git clone https://github.com/juancolonna/Sauim.git
cd sauim-detector
pip install .
```

This will also install required dependencies:  
- `librosa`  
- `numpy`  
- `scipy`  
- `tensorflow`  
- `tensorflow-hub`  
- `joblib`  
- `soundfile`  

---

## 🚀 Usage

The CLI entry point is `sauim-detector`.

```bash
sauim-detector path/to/audio.wav
```

### Options
- `--save-audio`, `-s`  
  If set, saves the filtered signal as a `.wav` file alongside the labels.  

---

## 📂 Outputs

1. **Detection labels** in [Audacity label format](https://manual.audacityteam.org/man/importing_and_exporting_labels.html):  
   ```
   start_time    end_time    label
   0.00          7.20        sauim
   10.00         15.50       sauim
   20.00         30.80       sauim
   ....
   ```

   These can be imported directly into Audacity via  
   **File → Import → Labels…**.

2. **Filtered audio** (optional, if `--save-audio` is used):  
   A `.wav` file containing the processed signal.  
   Example: `audio_filtered.wav`

---

## 📝 Example

```bash
# Run classification
sauim-detector recordings/example.wav

# Run classification and also save filtered audio
sauim-detector recordings/example.wav --save-audio
```

Output:

```
Total detections: 2
✅ Labels saved as: recordings/example_detections.txt
✅ Filtered signal saved as: recordings/example_filtered.wav
```

---

## ⚠️ Notes
- Input files must be in `.wav` format.  
- The default sampling rate is `32 kHz`. Files will be resampled automatically if needed.  
- Labels are generated based on classifier decisions (OCSVM) and they need manual validation on Audacity.
