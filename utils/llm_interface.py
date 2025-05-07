import os
from openai import OpenAI
from utils.logger import get_logger

logger = get_logger("LLM")

class LLMService:
    def __init__(self, agent_config):
        self.provider = agent_config.get("provider", "openai").lower()
        self.model = agent_config.get("model", "gpt-4")
        self.temperature = agent_config.get("temperature", 0.1)
        self.top_p = agent_config.get("top_p", 1.0)
        self.n = agent_config.get("n", 1)
        self.stop = agent_config.get("stop", None)
        self.max_tokens = agent_config.get("max_tokens", 1024)

        self.presence_penalty = agent_config.get("presence_penalty", 0.0)
        self.frequency_penalty = agent_config.get("frequency_penalty", 0.0)
        self.logit_bias = agent_config.get("logit_bias", None)
        self.user = agent_config.get("user", None)

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "gemini":
            gemini_key = os.getenv("GEMINI_API_NEOTEK_KEY")
            if not gemini_key:
                raise ValueError("GEMINI_API_NEOTEK_KEY environment variable not set.")
            self.client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        print(f"Moderl Parameters: \n {agent_config}")

    def chat(self, messages):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "n": self.n,
            "stop": self.stop,
            "max_tokens": self.max_tokens
        }

        if self.provider == "openai":
            kwargs.update({
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
                "logit_bias": self.logit_bias,
                "user": self.user
            })

        # 🚫 Remove all keys with None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        response = self.client.chat.completions.create(**kwargs)

        usage = getattr(response, "usage", None)
        if usage:
            logger.info(
                f"{self.provider.capitalize()} usage: prompt={usage.prompt_tokens}, "
                f"completion={usage.completion_tokens}, total={usage.total_tokens}"
            )
        return response
