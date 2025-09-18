import os,sys,torch
now_dir = os.getcwd()
sys.path.append(now_dir)
import re
import torch
import numpy as np
import logging
from scipy.io import wavfile
from tts_with_rvc.infer.vc.modules import VC
from tts_with_rvc.infer.vc.config import Config
from fairseq.data.dictionary import Dictionary

logger = logging.getLogger(__name__)


config = Config()
vc = VC(config)
last_model_path = ""
initial_is_half = config.is_half

torch.serialization.safe_globals([Dictionary])
torch.serialization.add_safe_globals([Dictionary])


def is_valid_device_format(device):
    if not isinstance(device, str):
        return False

    if device == "cpu":
        return True

    pattern = r"^(cuda|mps|dml):\d+$"
    return re.match(pattern, device) is not None

def resolve_output_path(output_dir_path, output_filename):
    if output_filename and os.path.isabs(output_filename):
        return output_filename

    filename = output_filename if output_filename else "out.wav"

    if output_dir_path:
        os.makedirs(output_dir_path, exist_ok=True)
        return os.path.join(output_dir_path, filename)
    
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    return os.path.join(temp_dir, filename)

def rvc_convert(model_path,
            f0_up_key=0,
            input_path=None, 
            output_dir_path=None,
            _is_half=None,
            f0method="rmvpe",
            file_index="",
            file_index2="",
            index_rate=1,
            filter_radius=3,
            resample_sr=0,
            rms_mix_rate=0.5,
            protect=0.33,
            verbose=False,
            device=None,
            output_filename = "out.wav"
          ):  
    '''
    Function to call for the rvc voice conversion.  All parameters are the same present in that of the webui

    Args: 
        model_path (str) : path to the rvc voice model you're using
        f0_up_key (int) : transpose of the audio file, changes pitch (positive makes voice higher pitch)
        input_path (str) : path to audio file (use wav file)
        output_dir_path (str) : path to output directory, defaults to parent directory in output folder
        _is_half (bool) : Determines half-precision
        f0method (str) : picks which f0 method to use: dio, harvest, crepe, rmvpe (requires rmvpe.pt)
        file_index (str) : path to file_index, defaults to None
        file_index2 (str) : path to file_index2, defaults to None.  #honestly don't know what this is for
        index_rate (int) : strength of the index file if provided
        filter_radius (int) : if >=3: apply median filtering to the harvested pitch results. The value represents the filter radius and can reduce breathiness.
        resample_sr (int) : quality at which to resample audio to, defaults to no resample
        rmx_mix_rate (int) : adjust the volume envelope scaling. Closer to 0, the more it mimicks the volume of the original vocals. Can help mask noise and make volume sound more natural when set relatively low. Closer to 1 will be more of a consistently loud volume
        protect (int) : protect voiceless consonants and breath sounds to prevent artifacts such as tearing in electronic music. Set to 0.5 to disable. Decrease the value to increase protection, but it may reduce indexing accuracy

    Returns:
        output_file_path (str) : file path and name of tshe output wav file

    '''
    global last_model_path, vc
    


    if not verbose:
        logging.getLogger('fairseq').setLevel(logging.ERROR)
        logging.getLogger('rvc').setLevel(logging.ERROR)

    if _is_half != None:
        is_half = _is_half
    else:
        is_half = initial_is_half

    output_file_path = resolve_output_path(output_dir_path, output_filename)


    change_config = False
    change_is_half = False
    change_forced_fp32 = False
    
    if device is not None:
        if device != "cpu" and not re.match(r"^(cuda|mps|dml):\d+$", device):
            raise ValueError(f"Invalid device format: '{device}'. Expected 'cuda:N', 'mps:N', 'dml:N' or 'cpu'")
        
        if device != vc.config.device:
            vc.config.device = device
            change_config = True

    if vc.config.is_half == True and f0method.lower() == "fcpe":
        vc.config.is_half = False
        change_forced_fp32 = True
    elif is_half != vc.config.is_half and f0method.lower() != "fcpe":
        vc.config.is_half = is_half
        change_is_half = True

    change_any = change_config or change_is_half or change_forced_fp32

    if last_model_path == "" or last_model_path != model_path or change_any:
        vc.get_vc(model_path)
        if change_config:
            logger.info(f"Changed device to: {device}")
        if change_is_half:
            logger.info(f"Changed half to: {is_half}")
        if change_forced_fp32:
            logger.info(f"Forced half to: {vc.config.is_half}")
        last_model_path = model_path
        
    tgt_sr, opt_wav =vc.vc_single(0,input_path,f0_up_key,None,f0method,file_index,file_index2,index_rate,filter_radius,resample_sr,rms_mix_rate,protect)

    wavfile.write(output_file_path, tgt_sr, opt_wav)
    saved_to = os.path.abspath(output_file_path)
    logger.info(f"Saved: {saved_to}")

    return saved_to


def main():
    rvc_convert(model_path="models\\DenVot.pth", input_path="out.wav")

if __name__ == "__main__":
    main()