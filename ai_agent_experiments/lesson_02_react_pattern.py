import re

from openai import AzureOpenAI

from ai_agent_experiments.config import Configuration


class ReaActAgent:
    def __init__(self, config: Configuration):
        self.client = AzureOpenAI(api_key=config.azure_open_ai_config["api_key"],
                                  azure_endpoint=config.azure_open_ai_config["azure_endpoint"],
                                  api_version=config.azure_open_ai_config["api_version"])
        self.model = config.azure_open_ai_config["model"]
        self.system_message = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()
        self.messages = [
            {
                "role": "system",
                "content": self.system_message
            }
        ]

    def __call__(self, query) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": query
            }
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
        return response.choices[0].message.content


def run_interactive_agent(query, max_turns=5) -> str:
    i = 0
    max_turns = 1 if max_turns <= 1 else max_turns
    agent = ReaActAgent(Configuration("../config.json"))
    action_re = re.compile(r'Action: (\w+): (.*)$')  # python regular expression to selection action
    while i < max_turns:
        i += 1
        llm_response = agent(query)
        action_match: re.Match | None = None
        for a in llm_response.split("\n"):
            if action_re.match(a):
                action_match = action_re.match(a)
                break
        if action_match:
            action_name = action_match.group(1)
            action_args = action_match.group(2)
            print(f"Action: {action_name} {action_args}")
            if action_name in known_actions:
                observation = known_actions[action_name](action_args)
                query = "Observation: {}".format(observation)
            else:
                return f"Error: Unknown action '{action_name}'"
        else:
            return llm_response
    return None


def calculate(what):
    # TODO: Replace eval() with safer parsing for production use
    # This is a simple implementation for learning purposes
    return eval(what)


def average_dog_weight(name):
    if name in "Scottish Terrier":
        return ("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return ("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return ("a toy poodles average weight is 7 lbs")
    else:
        return ("An average dog weights 50 lbs")


known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight
}

if __name__ == "__main__":
    res = run_interactive_agent("I have 2 dogs, a border collie and a scottish terrier. \
What is their combined weight")
    print(res)
