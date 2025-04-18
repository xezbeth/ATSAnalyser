# ATSAnalyser

This program takes a job description and ranks candidate resume according to relevency using LLM's.



# Installation
```
1. git clone https://github.com/xezbeth/ATSAnalyser.git
2. cd ATSAnalyser
3. pip install -r requirements.txt
4. streamlit run main.py
```

Once the streamlit app opens, you can type the desired job description into the text field and click the generate weighted job descriptino button.

Then select the number of threads(this indicates the number of resume to be analyzes at a time) and click analyse.

The result should appear at the top as a table with ranking.

# Diagram

```mermaid
stateDiagram-v2
    [*] --> ClientInput
    
    ClientInput: Client Input
    ClientInput: Job Description
    
    ClientInput --> DescriptorAI
    
    DescriptorAI: Descriptor AI
    DescriptorAI: Processes job description
    DescriptorAI: Creates weighted criteria
    
    DescriptorAI --> WeightedJobDescription
    WeightedJobDescription: Weighted Job Description
    WeightedJobDescription: Prioritized criteria
    WeightedJobDescription: Importance factors
    
    WeightedJobDescription --> GeneratorAI
    
    GeneratorAI: Generator AI
    GeneratorAI: Analyzes resumes against criteria
    GeneratorAI: Ranks candidates
    
    GeneratorAI --> RankedCandidates
    RankedCandidates: Ranked Candidates
    RankedCandidates: Scored resumes
    RankedCandidates: Matching rationales
    
    RankedCandidates --> ReflectorAI
    
    ReflectorAI: Reflector AI
    ReflectorAI: Critiques ranking
    ReflectorAI: Identifies improvements
    
    ReflectorAI --> Feedback
    Feedback: Feedback Loop
    Feedback: Ranking quality assessment
    Feedback: Suggested improvements
    
    Feedback --> ImprovementDecision
    
    ImprovementDecision: Quality Check
    ImprovementDecision: Evaluates if ranking meets quality threshold
    
    ImprovementDecision --> GeneratorAI: Needs improvement
    ImprovementDecision --> FinalOutput: Meets quality standards
    
    FinalOutput: Final Output
    FinalOutput: Optimized candidate ranking
    FinalOutput: Presented to client
    
    FinalOutput --> [*]
```

