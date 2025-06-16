import os
from crewai import Agent, Task, Crew, Process, LLM
from datetime import datetime

def setup_llm():
    api_key = os.getenv("CLARIFAI_PAT")
    if not api_key:
        raise ValueError("Please set the environment variable CLARIFAI_PAT with your Clarifai API key.")
    
    return LLM(
        model="openai/deepseek-ai/deepseek-chat/models/DeepSeek-R1-Distill-Qwen-7B",
        base_url="https://api.clarifai.com/v2/ext/openai/v1",
        api_key=api_key
    )

def create_research_agent(llm):
    return Agent(
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments and facts on a given topic",
        backstory="""You are a meticulous and insightful research analyst at a tech think tank.
        You specialize in identifying trends, gathering verified information,
        and presenting concise insights.""",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

def create_research_task(topic, agent):
    return Task(
        description=f"""Conduct a comprehensive analysis of '{topic}'.
        Identify key trends, breakthrough technologies, important figures, and potential industry impacts.
        Focus on factual and verifiable information.""",
        expected_output="A detailed analysis report in bullet points, including sources if possible.",
        agent=agent
    )

def run_research(topic, agent):
    task = create_research_task(topic, agent)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    return crew.kickoff()

def save_report(topic, report):
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic).lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_report_{safe_topic}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Research Report on: {topic}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*40 + "\n\n")

        # Convert result to string explicitly
        f.write(str(report))

    return filename


def main():
    print("=== Welcome to the Research Assistant ===\n")
    llm = setup_llm()
    researcher = create_research_agent(llm)

    while True:
        topic = input("Enter a research topic (or 'exit' to quit): ").strip()
        if topic.lower() in ["exit", "quit", "q"]:
            print("Goodbye! Thanks for using the Research Assistant.")
            break
        if not topic:
            print("Please enter a valid topic.")
            continue
        
        print(f"\nResearching '{topic}'...\nThis may take a moment, please wait...\n")
        try:
            result = run_research(topic, researcher)
            print("Research Completed!\n")
            print(result)
            
            filename = save_report(topic, result)
            print(f"\nReport saved to: {filename}\n")
        except Exception as e:
            print(f"Oops! Something went wrong during the research: {e}\n")

if __name__ == "__main__":
    main()
