from typing import Optional

from pipelex.cogt.exceptions import MissingDependencyError
from pipelex.cogt.llm.llm_models.llm_engine import LLMEngine
from pipelex.cogt.llm.llm_models.llm_platform import LLMPlatform
from pipelex.cogt.llm.llm_worker_internal_abstract import LLMWorkerInternalAbstract
from pipelex.cogt.llm.structured_output import StructureMethod
from pipelex.config import get_config
from pipelex.hub import get_plugin_manager
from pipelex.plugins.plugin_sdk_registry import PluginSdkHandle
from pipelex.reporting.reporting_protocol import ReportingProtocol


class LLMWorkerFactory:
    @staticmethod
    def make_llm_worker(
        llm_engine: LLMEngine,
        reporting_delegate: Optional[ReportingProtocol] = None,
    ) -> LLMWorkerInternalAbstract:
        llm_sdk_handle = PluginSdkHandle.get_for_llm_platform(llm_platform=llm_engine.llm_platform)
        plugin_sdk_registry = get_plugin_manager().plugin_sdk_registry
        llm_worker: LLMWorkerInternalAbstract
        match llm_engine.llm_platform:
            case LLMPlatform.OPENAI | LLMPlatform.AZURE_OPENAI | LLMPlatform.PERPLEXITY | LLMPlatform.XAI:
                from pipelex.plugins.openai.openai_factory import OpenAIFactory

                structure_method: Optional[StructureMethod] = None
                if get_config().cogt.llm_config.instructor_config.is_openai_structured_output_enabled:
                    structure_method = StructureMethod.INSTRUCTOR_OPENAI_STRUCTURED

                from pipelex.plugins.openai.openai_llm_worker import OpenAILLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=OpenAIFactory.make_openai_client(llm_platform=llm_engine.llm_platform),
                )

                llm_worker = OpenAILLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    structure_method=structure_method,
                    reporting_delegate=reporting_delegate,
                )
            case LLMPlatform.VERTEXAI:
                try:
                    import google.auth  # noqa: F401
                except ImportError as exc:
                    raise MissingDependencyError("google-auth-oauthlib", "google", "This dependency is required to connect to google.") from exc

                from pipelex.plugins.openai.openai_factory import OpenAIFactory
                from pipelex.plugins.openai.openai_llm_worker import OpenAILLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=OpenAIFactory.make_openai_client(llm_platform=llm_engine.llm_platform),
                )

                llm_worker = OpenAILLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    structure_method=StructureMethod.INSTRUCTOR_VERTEX_JSON,
                    reporting_delegate=reporting_delegate,
                )
            case LLMPlatform.CUSTOM_LLM:
                from pipelex.plugins.openai.openai_factory import OpenAIFactory
                from pipelex.plugins.openai.openai_llm_worker import OpenAILLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=OpenAIFactory.make_openai_client(llm_platform=llm_engine.llm_platform),
                )

                llm_worker = OpenAILLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    structure_method=StructureMethod.INSTRUCTOR_OPENAI_STRUCTURED,
                    reporting_delegate=reporting_delegate,
                )
            case LLMPlatform.ANTHROPIC | LLMPlatform.BEDROCK_ANTHROPIC:
                try:
                    import anthropic  # noqa: F401
                except ImportError as exc:
                    raise MissingDependencyError(
                        "anthropic",
                        "anthropic",
                        (
                            "The anthropic SDK is required to use Anthropic models via the anthropic client. "
                            "However, you can use Anthropic models through bedrock directly "
                            "by using the 'bedrock-anthropic-claude' llm family. (eg: bedrock-anthropic-claude)"
                        ),
                    ) from exc

                from pipelex.plugins.anthropic.anthropic_factory import AnthropicFactory
                from pipelex.plugins.anthropic.anthropic_llm_worker import AnthropicLLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=AnthropicFactory.make_anthropic_client(llm_platform=llm_engine.llm_platform),
                )

                llm_worker = AnthropicLLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    structure_method=StructureMethod.INSTRUCTOR_ANTHROPIC_TOOLS,
                    reporting_delegate=reporting_delegate,
                )
            case LLMPlatform.MISTRAL:
                try:
                    import mistralai  # noqa: F401
                except ImportError as exc:
                    raise MissingDependencyError(
                        "mistralai",
                        "mistral",
                        (
                            "The mistralai SDK is required to use Mistral models through the mistralai client. "
                            "However, you can use Mistral models through bedrock directly "
                            "by using the 'bedrock-mistral' llm family. (eg: bedrock-mistral-large)"
                        ),
                    ) from exc

                from pipelex.plugins.mistral.mistral_factory import MistralFactory
                from pipelex.plugins.mistral.mistral_llm_worker import MistralLLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=MistralFactory.make_mistral_client(),
                )

                llm_worker = MistralLLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    structure_method=StructureMethod.INSTRUCTOR_MISTRAL_TOOLS,
                    reporting_delegate=reporting_delegate,
                )
            case LLMPlatform.BEDROCK:
                try:
                    import aioboto3  # noqa: F401
                    import boto3  # noqa: F401
                except ImportError as exc:
                    raise MissingDependencyError(
                        "boto3,aioboto3", "bedrock", "The boto3 and aioboto3 SDKs are required to use Bedrock models."
                    ) from exc

                from pipelex.plugins.bedrock.bedrock_factory import BedrockFactory
                from pipelex.plugins.bedrock.bedrock_llm_worker import BedrockLLMWorker

                llm_sdk_instance = plugin_sdk_registry.get_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle
                ) or plugin_sdk_registry.set_llm_sdk_instance(
                    llm_sdk_handle=llm_sdk_handle,
                    llm_sdk_instance=BedrockFactory.make_bedrock_client(),
                )

                llm_worker = BedrockLLMWorker(
                    sdk_instance=llm_sdk_instance,
                    llm_engine=llm_engine,
                    reporting_delegate=reporting_delegate,
                )
        return llm_worker
