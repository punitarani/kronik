import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from kronik.logger import brain_logger as logger

model_id = "vikhyatk/moondream2"
revision = "2024-08-26"

# Load the vision model
logger.info(f"Loading model: {model_id} {revision}")
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, revision=revision)

# Load the tokenizer for the vision model
logger.info(f"Loading tokenizer: {model_id} {revision}")
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

# Move the vision model to GPU if available (preference: mps -> cuda -> cpu)
device = (
    "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
)
logger.info(f"Using device: {device} for {model_id} inference")
model.to(device)
