from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from typing import Annotated, List, Sequence
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
import io
import json

from Graphstate import GraphState, GeneratorAI, ReflectorAI, DescriptorAI



class ResumeAnalysisAI():


    def __init__(self, llm, generator_prompt, reflector_prompt,config):
        '''
        this class is used to analyze resumes based on a weighted job description.
        It uses a generator and reflector to analyze the resume and provide feedback.
        The generator is used to generate the analysis and the reflector is used to reflect on the analysis.
        The class uses a state graph to manage the flow of the analysis.
        
        '''
        
        self.llm = llm
        self.generator_prompt = generator_prompt
        self.reflector_prompt = reflector_prompt

        self.generator = self.generator_prompt | self.llm
        self.reflector = self.reflector_prompt | self.llm

        self.config = config
        self.output = None
        self.json_output = None
        self.prev_json_output = None

    def set_graph(self, graph: StateGraph):
        self.graph = graph


    async def Execute(self,weighted_job_description, resume):

        self.weighted_job_description = weighted_job_description
        self.resume = resume

        async for event in self.graph.astream(
            {
                "messages": [
                    HumanMessage(
                        content="Given the weighted job description, analyze the resume as per the instruction."
                        f"Weighted Job Description: {self.weighted_job_description}, Resume: {self.resume}"

        
                    )
                ],
            },
            self.config,
        ):
            print(event)
            print("---")
            #check if event is a generate event
            if "generate" in event:

                if self.output is not None:

                    self.prev_json_output = self.output

                self.output = event["generate"]["messages"][0].content
            

    def process_output(self, output):
        # Process the output as needed
        start_index = output.find("{")
        end_index = output.rfind("}")
        if start_index != -1 and end_index != -1:
            self.json_output = output[start_index+1:end_index]

        self.json_output = json.loads("{" + self.json_output + "}")


        return self.json_output
            
            