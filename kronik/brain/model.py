from transformers import AutoModelForCausalLM, AutoTokenizer

from kronik.logger import brain_logger as logger

model_id = "vikhyatk/moondream2"
revision = "2024-08-26"

logger.info(f"Loading model: {model_id} {revision}")
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, revision=revision)

logger.info(f"Loading tokenizer: {model_id} {revision}")
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
