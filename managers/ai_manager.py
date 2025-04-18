import logging
import time

from openai import OpenAI

from openai._exceptions import (
    APIError,
    OpenAIError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    UnprocessableEntityError,
    APIResponseValidationError,
)


class AIManager:

    def __init__(
        self,
        model: str = "o4-mini",
        instructions: str = "You are a helpful, step-by-step reasoning assistant.",
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        self.client = OpenAI()
        self.model = model
        self.instructions = instructions
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _format_history_for_openai_api(self, message_history: list[tuple[str, str]]) -> list[dict[str, str]]:
        formatted_input = []
        for sender, content in message_history:
            role = "assistant" if sender == "AI" else "user" if sender == "You" else "system" if sender == "System" else None
            if role:
                formatted_input.append({"role": role, "content": content})
        return formatted_input

    def get_response(self, message_history: list[tuple[str, str]], override_instructions: str | None = None) -> str:

        if not message_history:
            logging.error("Empty question passed to get_response()")
            raise ValueError("Question must be a non-empty string.")

        current_instructions = override_instructions or self.instructions

        formatted_input_array = self._format_history_for_openai_api(message_history)


        if not formatted_input_array or formatted_input_array[0].get("role") != "system":
             formatted_input_array.insert(0, {"role": "system", "content": current_instructions})
        elif formatted_input_array[0].get("role") == "system":
             formatted_input_array[0]["content"] = current_instructions

        payload = {
            "model": self.model,
            "input": formatted_input_array,
        }

        attempt = 0
        while True:
            try:
                logging.info(
                    "Calling Responses API [%s] (attempt %d): input messages %d",
                    self.model,
                    attempt + 1,
                    len(formatted_input_array),
                )
                resp = self.client.responses.create(**payload)
                logging.debug("API raw response: %r", resp)
                return resp.output_text.strip() if hasattr(resp, 'output_text') and resp.output_text else "No text response received."

            # Transient / retryable errors
            except (RateLimitError, APITimeoutError, APIConnectionError) as e:
                attempt += 1
                if attempt > self.max_retries:
                    logging.exception("Exceeded retries for transient error: %s", e)
                    raise
                wait = self.backoff_factor**attempt
                logging.warning(
                    "%s on attempt %d – retrying in %.1f seconds",
                    e.__class__.__name__,
                    attempt,
                    wait,
                )
                time.sleep(wait)

            # Client or configuration errors – do not retry
            except (
                BadRequestError,
                AuthenticationError,
                PermissionDeniedError,
                NotFoundError,
                ConflictError,
                UnprocessableEntityError,
                APIResponseValidationError,
            ) as e:
                logging.error(
                    "Non-retryable OpenAI error [%s]: %s", e.__class__.__name__, e
                )
                raise

            # Server‑side errors (5xx) or unknown status codes
            except (APIStatusError, InternalServerError) as e:
                logging.exception(
                    "Server error [%s], giving up: %s", e.__class__.__name__, e
                )
                raise

            # Any other OpenAIError
            except OpenAIError as e:
                logging.exception("OpenAIError in get_response: %s", e)
                raise

            # Catch‑all
            except Exception as e:
                logging.exception("Unexpected error in AIManager.get_response: %s", e)
                raise
