"""
Local, fully-offline image captioning fallback (used only when GEMINI_API_KEY
is not configured). Heavy deps (torch/transformers) are imported lazily so
that the rest of the app can run without them installed when running in
Gemini-only mode.
"""
from PIL import Image


class ImageCaptionModel:
    def __init__(self, device: str = "cpu") -> None:
        try:
            import torch
            from transformers import BlipProcessor, BlipForConditionalGeneration
        except ImportError as exc:
            raise RuntimeError(
                "Local fallback captioning requires 'torch' and 'transformers'. "
                "Install them with: pip install -r requirements-local.txt"
            ) from exc

        self._torch = torch
        self.device = torch.device(device)
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        self.model.eval()

    def generate_caption(self, image: Image.Image) -> str:
        # Ensure image is RGB
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        # Move tensors to model device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        # Use stronger generation settings to encourage detailed captions
        gen_kwargs = dict(
            max_new_tokens=64,
            num_beams=6,
            do_sample=True,
            top_p=0.95,
            temperature=0.8,
            no_repeat_ngram_size=3,
        )
        with self._torch.no_grad():
            # Some transformers accept max_new_tokens, others max_length — provide both for compatibility
            try:
                output_ids = self.model.generate(**inputs, **gen_kwargs)
            except TypeError:
                # fallback if model.generate doesn't accept max_new_tokens
                output_ids = self.model.generate(**inputs, max_length=256, num_beams=6, no_repeat_ngram_size=3)
        # Use processor.tokenizer if available to decode
        if hasattr(self.processor, "tokenizer"):
            caption = self.processor.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        else:
            caption = self.processor.decode(output_ids[0], skip_special_tokens=True)

        # Post-process: ensure caption is not overly short; if it is, try a second pass without sampling
        caption = caption.strip()
        if len(caption.split()) < 6:
            # Retry with deterministic beams to expand detail
            with self._torch.no_grad():
                try:
                    output_ids = self.model.generate(**inputs, num_beams=8, max_new_tokens=80, no_repeat_ngram_size=3, early_stopping=True)
                except TypeError:
                    output_ids = self.model.generate(**inputs, num_beams=8, max_length=300, no_repeat_ngram_size=3)
            if hasattr(self.processor, "tokenizer"):
                caption2 = self.processor.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
            else:
                caption2 = self.processor.decode(output_ids[0], skip_special_tokens=True).strip()
            if len(caption2.split()) > len(caption):
                caption = caption2

        return caption.strip()
