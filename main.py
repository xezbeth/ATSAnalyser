

import streamlit as st
from ResumeAnalysisAI import ResumeAnalysisAI
from Graphstate import GraphState, GeneratorAI, ReflectorAI, DescriptorAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import io
import asyncio
import threading
import pandas as pd


groq_api = st.text_input("Enter your Groq API key", type="password")

if not groq_api:
    st.warning("Please enter your Groq API key to continue.")
    st.stop()



llm = ChatGroq(
    model="gemma2-9b-it",
    api_key=groq_api,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

# llm = ChatOpenAI(
#     model="gpt-4o-mini-2024-07-18",
#     openai_api_key=openai_api,
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

#create the generator and reflector AI
generator_ai = GeneratorAI(prompt_path = "generator_prompt.txt")
reflector_ai = ReflectorAI(prompt_path = "reflector_prompt.txt")

config = {"configurable": {"thread_id": "1"}}

# Create the ResumeAnalysisAI object
resume_analysis_ai = ResumeAnalysisAI(
    llm=llm,
    generator_prompt = generator_ai.prompt,
    reflector_prompt = reflector_ai.prompt,
    config=config,
)



graph_state = GraphState(
    generator=resume_analysis_ai.generator,
    reflector=resume_analysis_ai.reflector,
)

graph = graph_state.build_graph()

resume_analysis_ai.set_graph(graph)

# Create the DescriptorAI object
descriptor_ai = DescriptorAI(prompt_path = "descriptor_prompt.txt")

#get the job description from the file
with io.open("job_description_raw.txt",mode= "r",encoding="utf-8") as file:
    job_description_raw = file.read()


job_description = descriptor_ai.weighted_job_description

#get the resume from the file
with io.open("resume.txt",mode= "r",encoding="utf-8") as file:
    resume = file.read()



json_ouputs = []

# run the analysis in a separate thread
async def run_analysis(config,resume):
    '''
    this function is used to run the analysis.
    It takes the config and resume as input and runs the analysis in a separate thread.
    '''

    resume_analysis_ai.config = config
    # Execute the analysis
    await  resume_analysis_ai.Execute(job_description, resume)


    json_ouput = resume_analysis_ai.process_output(resume_analysis_ai.output)
    if json_ouput == {}:
        json_output = resume_analysis_ai.process_output(resume_analysis_ai.prev_json_output)

    #display the json output to streamlit
    #st.write(resume_analysis_ai.json_output)
    json_ouputs.append(json_output)




# Create a thread for each analysis
threads = []
#we would get all the resumes downloaded in the folder and analyze them
#for now we are just analyzing one resume
resume_list = [resume]
resumes_analysed = 0



def buffer_threaded_analysis(no_threads):
    '''
    This function is used to buffer the threaded analysis.
    It takes the number of threads as input and runs the analysis in a separate thread.
    this function keeps track of the number of resumes analysed and the number of resumes left to be analysed.
    It also creates a thread for each analysis and waits for all threads to complete.
    '''
    global resume_list
    global resumes_analysed

    # Create and start threads
    total_resumes = len(resume_list)
    
    #analyze only the number of resumes that can be analyzed in the given number of threads

    for i in range(0,total_resumes):

        resumes_left = total_resumes - resumes_analysed
        threads_used = min(resumes_left, no_threads)

        multithreaded_analysis(threads_used, resume_list[resumes_analysed:resumes_analysed + threads_used])
        resumes_analysed += threads_used





def multithreaded_analysis(no_threads = 1, resumes = []):
    '''
    This function is used to run the analysis in a separate thread.
    It takes the number of threads and the resumes as input and runs the analysis in a separate thread.
    '''


    for i in range(no_threads):
        thread = threading.Thread(target=run_threaded_analysis, args=(i,resumes[i]))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


    with st.container():
        st.header("Resume Analysis Results")
        # Display the results in a table
        df = pd.DataFrame(json_ouputs)
        st.write(df)


def run_threaded_analysis(thread_id, resume):
    '''
    This function is used to run the analysis in a separate thread.
    '''
    print(f"Thread {thread_id} started")
    config = {"configurable": {"thread_id": str(thread_id)}}
    asyncio.run(run_analysis(config, resume))



with st.container():
    st.header("1.Job Description")
    #text field for job description
    st.text_area("Enter the job requirements for the AI to analyze", job_description_raw, height=300)

    st.button("Generate weighted requirements", on_click=descriptor_ai.ExecuteDescriptor, args=(job_description_raw,llm))

with st.container():
    st.header("2.Analyze Resume")
    #text field for resume
    no_threads = st.slider("No of threads:(number of resume to be analyzed at a time)", 1, 20, 1)

    #run threaded analysis
    st.button("Run Analysis", on_click = buffer_threaded_analysis, args=(no_threads,))

















