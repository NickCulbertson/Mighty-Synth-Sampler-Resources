import os
import subprocess
import re
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

# Path to wavpack tool — run `which wavpack` in Terminal to confirm your path.
WAVPACK_PATH = '/usr/local/bin/wavpack'

# WavPack compression flags
WAVPACK_FLAGS = ['-q', '-r', '-b24']

# Set to True to peak-normalize each WAV to 0 dB before converting.
# When True, the script modifies your original .wav files in place during normalization.
# When False, your .wav files are untouched and only the .wv versions are written.
NORMALIZE_BEFORE_CONVERT = False

# Function to calculate the gain needed to normalize to 0 dB peak
def calculate_gain(input_file):
    try:
        # Run ffmpeg with volumedetect filter to get the maximum volume
        result = subprocess.run(
            [
                "ffmpeg",
                "-i", input_file,
                "-af", "volumedetect",
                "-f", "null",
                "-",
            ],
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Search for the max_volume in the output
        max_volume_match = re.search(r"max_volume: (-?\d+(\.\d+)?) dB", result.stderr)
        if max_volume_match:
            max_volume = float(max_volume_match.group(1))
            # Calculate the gain needed to reach 0 dB
            gain = -max_volume
            return gain
        else:
            print(f"Could not determine max volume for {input_file}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error calculating gain for {input_file}: {e.stderr}")
        return None

# Function to normalize a single WAV file
def normalize_audio_peak(input_file):
    try:
        # Calculate the required gain
        gain = calculate_gain(input_file)
        
        # Skip if gain couldn't be calculated
        if gain is None:
            print(f"Skipping normalization for {input_file}: Could not calculate gain")
            return input_file  # Return the original file path
        
        # Skip if the file is already normalized (gain is very small)
        if abs(gain) < 0.1:  # If gain adjustment is less than 0.1 dB, consider it already normalized
            print(f"Skipping normalization for {input_file}: Already normalized (gain adjustment: {gain} dB)")
            return input_file  # Return the original file path
        
        # Create a temporary file in the same directory as the input file
        dir_path = os.path.dirname(input_file)
        with tempfile.NamedTemporaryFile(dir=dir_path, suffix='.wav', delete=False) as temp_file:
            temp_output_file = temp_file.name
        
        # Use ffmpeg to normalize the audio
        try:
            subprocess.run([
                "ffmpeg",
                "-i", input_file,
                "-af", f"volume={gain}dB",
                "-y",  # Overwrite output file
                temp_output_file
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Replace the original file with the normalized version
            os.replace(temp_output_file, input_file)
            print(f"Peak Normalized: {input_file} (applied gain: {gain} dB)")
            return input_file  # Return the normalized file path
            
        except subprocess.SubprocessError as e:
            print(f"Error normalizing {input_file}: {str(e)}")
            # Clean up temporary file if it exists
            if os.path.exists(temp_output_file):
                os.remove(temp_output_file)
            return input_file  # Return the original file path even if normalization failed
        
    except Exception as e:
        print(f"Unexpected error processing {input_file}: {str(e)}")
        return input_file  # Return the original file path

# Function to convert WAV to WV
def convert_to_wv(wav_path):
    try:
        wv_path = os.path.splitext(wav_path)[0] + '.wv'
        print(f"Converting: {wav_path} → {wv_path}")
        
        # Run wavpack command
        result = subprocess.run([WAVPACK_PATH] + WAVPACK_FLAGS + [wav_path],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               check=True)
        
        # Check if the WV file was created successfully
        if os.path.exists(wv_path):
            print(f"Successfully converted: {wv_path}")
            # Uncomment the line below to also delete the original WAV file after a successful conversion.
            # Leave commented to keep both the .wav and .wv side by side (Mighty Synth Sampler will
            # automatically prefer the .wv when both are present).
            # os.remove(wav_path)
            return True
        else:
            print(f"Failed to create WV file: {wv_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error converting {wav_path} to WV: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error converting {wav_path}: {str(e)}")
        return False

# Function to process a single file (optionally normalize, then convert)
def process_file(wav_path):
    try:
        # Optionally peak-normalize the WAV file in place
        if NORMALIZE_BEFORE_CONVERT:
            path_to_convert = normalize_audio_peak(wav_path)
        else:
            path_to_convert = wav_path

        # Then convert to WV format
        if path_to_convert:
            convert_to_wv(path_to_convert)

    except Exception as e:
        print(f"Error processing {wav_path}: {str(e)}")

# Function to process all WAV files in a directory and subdirectories
def process_directory(directory, max_workers=4):
    # Collect all WAV files
    wav_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.wav'):
                wav_files.append(os.path.join(root, file))
    
    if not wav_files:
        print(f"No WAV files found in {directory} or its subdirectories.")
        return
    
    print(f"Found {len(wav_files)} WAV files to process.")
    
    # Process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_file, wav_files)
    
    print("Processing complete!")

# Entry point
if __name__ == "__main__":
    current_directory = '.'
    process_directory(current_directory)
