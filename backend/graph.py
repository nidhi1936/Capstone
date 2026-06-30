from langgraph.graph import START, END, StateGraph
from state import SupportState
from nodes import fit_analyse, resume_rewrite,cover_letter_draft,mock_interview,collect_output

#BUILDING GRAPH
builder = StateGraph(SupportState)
#NODES
builder.add_node("fit_analyse", fit_analyse)
builder.add_node("resume_rewrite", resume_rewrite)
builder.add_node("cover_letter_draft", cover_letter_draft)
builder.add_node("mock_interview", mock_interview)
builder.add_node("collect_output",collect_output)

#EDGES
builder.add_edge(START, "fit_analyse")
builder.add_edge("fit_analyse","resume_rewrite")
builder.add_edge("fit_analyse", "cover_letter_draft")
builder.add_edge("fit_analyse", "mock_interview")
builder.add_edge("resume_rewrite", "collect_output")
builder.add_edge("cover_letter_draft","collect_output")
builder.add_edge("mock_interview","collect_output")
builder.add_edge("collect_output",END)

graph = builder.compile()
#result=graph.invoke({"resume":"I am a software Engineer with 10 years of experience in Java","job_description":"Needed an Software Developer"})
#result=graph.invoke({"resume":"resume.pdf","job_description":"Needed an Software Developer"})
#print(result)