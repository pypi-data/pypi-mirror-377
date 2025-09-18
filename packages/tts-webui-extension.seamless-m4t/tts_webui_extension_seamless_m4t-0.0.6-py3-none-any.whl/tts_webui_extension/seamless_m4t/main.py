import gradio as gr
import torch
import torchaudio

from extension_seamless_m4t.language_code_to_name import (
    text_source_languages,
    speech_target_languages,
    text_source_codes,
    speech_target_codes,
)

from tts_webui.decorators.gradio_dict_decorator import dictionarize
from tts_webui.utils.randomize_seed import randomize_seed_ui
from tts_webui.utils.manage_model_state import manage_model_state
from tts_webui.utils.list_dir_models import unload_model_button
from tts_webui.decorators.decorator_apply_torch_seed import decorator_apply_torch_seed
from tts_webui.decorators.decorator_log_generation import decorator_log_generation
from tts_webui.decorators.decorator_save_metadata import decorator_save_metadata
from tts_webui.decorators.decorator_save_wav import decorator_save_wav
from tts_webui.decorators.decorator_add_base_filename import decorator_add_base_filename
from tts_webui.decorators.decorator_add_date import decorator_add_date
from tts_webui.decorators.decorator_add_model_type import decorator_add_model_type
from tts_webui.decorators.log_function_time import log_function_time
from tts_webui.extensions_loader.decorator_extensions import (
    decorator_extension_outer,
    decorator_extension_inner,
)


@manage_model_state("seamless")
def get_model(model_name="", device=torch.device("cpu"), quantize=False):
    from transformers import AutoProcessor, SeamlessM4Tv2Model

    if quantize:
        from transformers import QuantoConfig

        quantization_config = QuantoConfig(weights="int8")
    else:
        quantization_config = None
    return SeamlessM4Tv2Model.from_pretrained(
        model_name, device_map="cuda:0", quantization_config=quantization_config
    ).to(device), AutoProcessor.from_pretrained(model_name)


@decorator_extension_outer
@decorator_apply_torch_seed
@decorator_save_metadata
@decorator_save_wav
@decorator_add_model_type("seamless")
@decorator_add_base_filename
@decorator_add_date
@decorator_log_generation
@decorator_extension_inner
@log_function_time
def seamless_translate(text, src_lang_name, tgt_lang_name, **kwargs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model, processor = get_model("facebook/seamless-m4t-v2-large", device)
    src_lang = text_source_codes[text_source_languages.index(src_lang_name)]
    tgt_lang = speech_target_codes[speech_target_languages.index(tgt_lang_name)]
    text_inputs = processor(text=text, src_lang=src_lang, return_tensors="pt").to(
        device
    )
    audio_array_from_text = (
        model.generate(**text_inputs, tgt_lang=tgt_lang)[0].cpu().squeeze()
    )
    sample_rate = model.config.sampling_rate

    return {"audio_out": (sample_rate, audio_array_from_text.numpy())}


@decorator_extension_outer
@decorator_apply_torch_seed
@decorator_save_metadata
@decorator_save_wav
@decorator_add_model_type("seamless")
@decorator_add_base_filename
@decorator_add_date
@decorator_log_generation
@decorator_extension_inner
@log_function_time
def seamless_translate_audio(audio, tgt_lang_name, **kwargs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model, processor = get_model("facebook/seamless-m4t-v2-large", device)
    orig_freq, audio = audio
    sample_rate = model.config.sampling_rate

    # Convert numpy array to torch tensor
    audio_tensor = torch.from_numpy(audio).float()

    # Handle different audio shapes (mono vs stereo)
    if audio_tensor.dim() == 1:
        # Mono audio - add channel dimension
        audio_tensor = audio_tensor.unsqueeze(0)
    elif audio_tensor.dim() == 2:
        # Stereo audio - convert to mono by averaging channels
        if audio_tensor.shape[0] == 2:  # Shape: [channels, samples]
            audio_tensor = audio_tensor.mean(dim=0, keepdim=True)
        elif audio_tensor.shape[1] == 2:  # Shape: [samples, channels]
            audio_tensor = audio_tensor.mean(dim=1, keepdim=True).T
        else:
            # If it's not clearly stereo, take the first channel
            audio_tensor = (
                audio_tensor[0:1]
                if audio_tensor.shape[0] < audio_tensor.shape[1]
                else audio_tensor[:, 0:1].T
            )

    # Resample to 16kHz
    audio_resampled = torchaudio.functional.resample(
        audio_tensor, orig_freq=orig_freq, new_freq=16_000
    )

    tgt_lang = speech_target_codes[speech_target_languages.index(tgt_lang_name)]
    audio_inputs = processor(audios=audio_resampled, return_tensors="pt").to(device)
    audio_array_from_audio = (
        model.generate(**audio_inputs, tgt_lang=tgt_lang)[0].cpu().squeeze()
    )

    return {"audio_out": (sample_rate, audio_array_from_audio.numpy())}


def ui():
    gr.Markdown(
        """
    # Seamless Demo
    To use it, simply enter your text, and click "Translate".
    The model will translate the text into the target language, and then synthesize the translated text into speech.
    It uses the [SeamlessM4Tv2Model](https://huggingface.co/facebook/seamless-m4t-v2-large) model from HuggingFace.
    """
    )
    with gr.Row(equal_height=False):
        with gr.Column():
            with gr.Tab(label="Text to Speech"):
                seamless_input = gr.Textbox(lines=2, label="Input Text")
                source_language = gr.Dropdown(
                    choices=text_source_languages,  # type: ignore
                    label="Source Language",
                    value="English",
                    type="value",
                )
                target_language = gr.Dropdown(
                    choices=speech_target_languages,  # type: ignore
                    label="Target Language",
                    value="Mandarin Chinese",
                    type="value",
                )
                button = gr.Button("Translate Text to Speech")
            with gr.Tab(label="Audio to Speech"):
                input_audio = gr.Audio(
                    sources="upload",
                    type="numpy",
                    label="Input Audio",
                )
                target_language_audio = gr.Dropdown(
                    choices=speech_target_languages,  # type: ignore
                    label="Target Language (Not all are supported)",
                    value="Mandarin Chinese",
                    type="value",
                )
                button2 = gr.Button("Translate Audio to Speech")

        with gr.Column():
            audio_out = gr.Audio(label="Output Audio")

            seed, randomize_seed_callback = randomize_seed_ui()
            unload_model_button("seamless")

    input_dict = {
        seamless_input: "text",
        source_language: "src_lang_name",
        target_language: "tgt_lang_name",
        seed: "seed",
    }

    input_dict2 = {
        input_audio: "audio",
        target_language_audio: "tgt_lang_name",
    }

    output_dict = {
        "audio_out": audio_out,
    }

    button.click(
        **randomize_seed_callback,
    ).then(
        **dictionarize(
            fn=seamless_translate,
            inputs=input_dict,
            outputs=output_dict,
        ),
        api_name="seamless",
    )

    button2.click(
        **randomize_seed_callback,
    ).then(
        **dictionarize(
            fn=seamless_translate_audio,
            inputs=input_dict2,
            outputs=output_dict,
        ),
        api_name="seamless_audio",
    )


def extension__tts_generation_webui():
    ui()

    return {
        "package_name": "extension_seamless_m4t",
        "name": "Seamless M4T",
        "requirements": "git+https://github.com/rsxdalv/extension_seamless_m4t@main",
        "description": "SeamlessM4T is a multilingual and multimodal translation model supporting text and speech",
        "extension_type": "interface",
        "extension_class": "text-to-speech",
        "author": "Facebook",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/facebookresearch/seamless_communication",
        "extension_website": "https://github.com/rsxdalv/extension_seamless_m4t",
        "extension_platform_version": "0.0.1",
    }


if __name__ == "__main__":
    if "demo" in locals():
        locals()["demo"].close()  # type: ignore
    with gr.Blocks() as demo:
        with gr.Tab("Seamless M4Tv2", id="seamless"):
            ui()

    demo.launch(
        server_port=7771,
    )
