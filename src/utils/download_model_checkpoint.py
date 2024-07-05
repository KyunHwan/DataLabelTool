import wget
import os
import re
import urllib.error
from urllib.parse import urlparse

def download_file(url: str, dest: str):
    try:
        wget.download(url, dest)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError("Error 404: File not found.")
        elif e.code == 403:
            raise ValueError("Error 403: Forbidden.")
        else:
            raise ValueError(f"HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        if "timed out" in str(e.reason):
            raise ValueError("Error: Connection timed out.")
        else:
            raise ValueError(f"URL Error: {e.reason}")
    except Exception as e:
        raise ValueError(f"Unexpected Error: {e}")

def get_model_type_from_model_checkpoint(model_checkpoint: str):
    filename= os.path.basename(model_checkpoint)
    pattern = r"sam_(.*?)_[a-zA-Z0-9]+\.pth"
    match = re.search(pattern, filename)

    if match: return match.group(1)
    else: return None

def get_filename_from_url(url: str):
    """
    example: 
        if url="https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        returns sam_vit_h_4b8939.pth
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    return os.path.basename(path)

def get_checkpoint(current_script_dir: str, url: str=""):
    # Loads the Segment Anything Model
    model_checkpoint_dir = os.path.join(current_script_dir, 'segment_anything_checkpoint')
    model_checkpoint = None
    try:
        print("Looking for Segment Anything Model checkpoint file...\n")
        model_checkpoint = os.path.join(model_checkpoint_dir, 
                                        os.listdir(model_checkpoint_dir)[0])
        print("Model checkpoint found!\n")
    except:
        print("Segment Anything model checkpoint not found!\n")
        print("Trying to download model checkpoint...\n")
        if not os.path.exists(model_checkpoint_dir):
            os.mkdir(model_checkpoint_dir)

        # Extract the filename from url
        filename = get_filename_from_url(url)
        model_checkpoint = os.path.join(model_checkpoint_dir, filename)
        try:
            download_file(url=url, dest=model_checkpoint)
            print("\nModel checkpoint successfully downloaded!\n")
        except:
            print("Please manually download model checkpoint for model type vit_h \
                  inside segment_anything_checkpoint folder...\n")
            return None
    
    return model_checkpoint