from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from ai_agent_experiments.config import Configuration

# This is a simple example of using the AzureAIChatCompletionsModel from langchain-azure-ai
# to generate a personality summary and fun facts based on provided information.

if __name__ == "__main__":
    config = Configuration("../config.json")
    model = AzureAIChatCompletionsModel(model=config.client_config["model"],
                                        credential=config.client_config["api_key"],
                                        endpoint=config.client_config["inference_endpoint"],
                                        )
    ada_info = """
    Adal Lambag is a fictional character from a fictional book named "The Lamb of Adal". Adal Lambag is a young woman who is a member of a family.
    She is a cyborg who has a secret identity. She is a member of a secret organization that fights against evil forces.
    She has a large interest in technology and art. She is never afraid to explore new ideas. She is always ready to learn new things.
    She had 3 eyes and 1 ear.
    """
    system_template = "Given the following details about a personality :{information}, write a short summary of their personality and share 2 fun facts about them."
    prompt_template = PromptTemplate(input_variables=["information"], template=system_template)

    # Below is the LangChain chain in Langchain Expression Language. runnable interface -> call invoke method of each member of the chain
    # `Chain` is a developer-defined control flow unlike an agent where LLM determines the next step
    chain = prompt_template | model | StrOutputParser()
    print(chain.invoke({"information": ada_info}))
