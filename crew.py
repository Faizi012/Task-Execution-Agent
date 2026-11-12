
from crewai import Crew, Process

from agents import (
    planner_agent,
    researcher_agent,
    executor_agent,
    reviewer_agent
)

from tasks import create_tasks


def execute_task(user_task):

    # Create tasks for the given user instruction
    task_list = create_tasks(
        planner_agent=planner_agent,
        researcher_agent=researcher_agent,
        executor_agent=executor_agent,
        reviewer_agent=reviewer_agent,
        user_task=user_task
    )

    # Create the crew
    task_crew = Crew(
        agents=[
            planner_agent,
            researcher_agent,
            executor_agent,
            reviewer_agent
        ],

        tasks=task_list,

        process=Process.sequential,

        verbose=True
    )

    # Start execution
    result = task_crew.kickoff()

    return result.raw
