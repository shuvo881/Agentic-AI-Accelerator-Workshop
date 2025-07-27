import asyncio
import logging, os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAITextToImage
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.openapi_plugin import OpenAPIFunctionExecutionParameters
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import KernelArguments
#Import Modules

# Add Logger
logger = logging.getLogger(__name__)

load_dotenv(override=True)

chat_history = ChatHistory()

def initialize_kernel():
    #Challene 02 - Add Kernel
    kernel = Kernel()
    
    #Challenge 02 - Chat Completion Service
    #//Add Azure AI Foundry Chat Completion
    chat_completion_service = AzureChatCompletion(
        deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],  
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], # Used to point to your service
        # service_id="my-service-id", # Optional; for targeting specific services within Semantic Kernel
    )
    # Retrieve the chat completion service by id
    # chat_completion_service = AzureChatCompletion(service_id="my-service-id")
    
    
    #Challenge 05 - Add Text Embedding service for semantic search
    #Challenge 07 - Add DALL-E image generation service
    # Retrieve the default inference settings
    # chat_completion_service = kernel.get_service(type=ChatCompletionClientBase)
    kernel.add_service(chat_completion_service)
    return kernel


async def process_message(user_input):
    kernel = initialize_kernel()

    #Challenge 03 and 04 - Services Required
    #Challenge 03 - Create Prompt Execution Settings



    # Challenge 03 - Add Time Plugin
    # Placeholder for Time plugin

    # Challenge 04 - Import OpenAPI Spec
    # Placeholder for OpenAPI plugin


    # Challenge 05 - Add Search Plugin


    # Challenge 06- Semantic kernel filters

    # Challenge 07 - Text To Image Plugin
    # Placeholder for Text To Image plugin

    # Start Challenge 02 - Sending a message to the chat completion service by invoking kernel

    #return result

def reset_chat_history():
    global chat_history
    chat_history = ChatHistory()
