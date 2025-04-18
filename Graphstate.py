from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class State(TypedDict):
    messages: Annotated[list, add_messages]


class GraphState():

    def __init__(self, generator, reflector):
        '''
        This class is used to create a state graph for the generator and reflector.
        It uses the generator and reflector to create a state graph.
        The state graph is used to manage the flow of the analysis.
        
        '''
        self.generator = generator
        self.reflector = reflector


    async def generation_node(self,state: State) -> State:
        return {"messages": [await self.generator.ainvoke(state["messages"])]}


    async def reflection_node(self,state: State) -> State:
        # Other messages we need to adjust
        cls_map = {"ai": HumanMessage, "human": AIMessage}
        # First message is the original user request. We hold it the same for all nodes
        translated = [state["messages"][0]] + [
            cls_map[msg.type](content=msg.content) for msg in state["messages"][1:]
        ]
        res = await self.reflector.ainvoke(translated)
        # We treat the output of this as human feedback for the generator
        return {"messages": [HumanMessage(content=res.content)]}
    
    def build_graph(self) -> StateGraph:


        builder = StateGraph(State)
        builder.add_node("generate", self.generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.add_edge(START, "generate")

        def should_continue(state: State):
            if len(state["messages"]) > 6:
                # End after 3 iterations
                return END
            return "reflect"


        builder.add_conditional_edges("generate", should_continue)
        builder.add_edge("reflect", "generate")
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        return graph
    

class GeneratorAI():

    def __init__(self, prompt_path: str = "generator_prompt.txt"):
        '''
        This class is used to create a generator AI.
        It uses the prompt path to create a generator AI.
        The generator AI is used to generate the analysis.
        '''

        self.prompt_path = prompt_path

        assert self.prompt_path is not None, "Prompt path cannot be None"
        #ensure file exists
        try:
            with open(self.prompt_path, "r") as file:
                gen_prompt = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file {self.prompt_path} not found")


        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    gen_prompt,

                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )


class ReflectorAI():

    def __init__(self, prompt_path: str = "reflector_prompt.txt"):
        '''
        This class is used to create a reflector AI.
        It uses the prompt path to create a reflector AI.
        The reflector AI is used to reflect on the analysis.
        '''

        self.prompt_path = prompt_path

        assert self.prompt_path is not None, "Prompt path cannot be None"
        #ensure file exists
        try:
            with open(self.prompt_path, "r") as file:
                ref_prompt = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file {self.prompt_path} not found")

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    ref_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )



class DescriptorAI():

    def __init__(self, prompt_path: str = "descriptor_prompt.txt"):
        '''
        This class is used to create a descriptor AI.
        It uses the prompt path to create a descriptor AI.
        The descriptor AI is used to extract the requirements from the job description.
        '''

        self.weighted_job_description = ""

        self.prompt_path = prompt_path

        assert self.prompt_path is not None, "Prompt path cannot be None"
        #ensure file exists
        try:
            with open(self.prompt_path, "r") as file:
                desc_prompt = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file {self.prompt_path} not found")

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    desc_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )


    def ExecuteDescriptor(self, job_description,llm):

        # Ensure the job description is not None or empty
        if not job_description:
            raise ValueError("Job description cannot be None or empty")
        
        request = HumanMessage(
        content="Given a random job description, extract the requirements from it. this is a test, so just use some random job description." +
        job_description,
            )
        self.descriptor = self.prompt | llm
        for chunk in self.descriptor.stream({"messages": [request]}):
            print(chunk.content, end="")
            self.weighted_job_description += chunk.content

        return self.weighted_job_description



