from typing import Optional, List, Union, Tuple

from backboard.configuration import Configuration
from backboard.api_client import ApiClient
from backboard.api.assistants_api import AssistantsApi
from backboard.api.threads_api import ThreadsApi
from backboard.api.documents_api import DocumentsApi
from backboard.models.assistant_create import AssistantCreate


class Backboard:
    """Simple Backboard client.

    Example:
        bb = Backboard(api_key="sk_...", base_url="https://backboard.io/api")
        assistant = bb.create_assistant(name="Support Bot", description="Helps users")
        thread = bb.create_thread(assistant.assistant_id)
        msg = bb.send_message(thread.thread_id, content="Hello")
    """

    def __init__(self, api_key: str, base_url: str = "https://backboard.io/api") -> None:
        config = Configuration(host=base_url)
        config.api_key["APIKeyHeader"] = api_key
        self._client = ApiClient(config)
        self.assistants = AssistantsApi(self._client)
        self.threads = ThreadsApi(self._client)
        self.documents = DocumentsApi(self._client)

    def create_assistant(self, name: str, description: Optional[str] = None, tools: Optional[list] = None):
        return self.assistants.create_assistant_assistants_post(
            AssistantCreate(name=name, description=description, tools=tools)
        )

    def create_thread(self, assistant_id: str):
        return self.assistants.create_thread_for_assistant_assistants_assistant_id_threads_post(
            assistant_id, {}
        )

    def send_message(
        self,
        thread_id: str,
        content: Optional[str] = None,
        files: Optional[List[Union[bytes, str, Tuple[str, bytes]]]] = None,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        stream: Optional[bool] = None,
        hide_tool_events: Optional[bool] = True,
    ):
        return self.threads.add_message_to_thread_threads_thread_id_messages_post(
            thread_id=thread_id,
            content=content,
            llm_provider=llm_provider,
            model_name=model_name,
            stream=stream,
            files=files,
            hide_tool_events=hide_tool_events,
        )

    def upload_document_to_thread(self, thread_id: str, file: Union[bytes, str, Tuple[str, bytes]]):
        return self.documents.upload_document_to_thread_threads_thread_id_documents_post(thread_id, file)

    def upload_document_to_assistant(self, assistant_id: str, file: Union[bytes, str, Tuple[str, bytes]]):
        return self.assistants.upload_document_to_assistant_assistants_assistant_id_documents_post(assistant_id, file)
