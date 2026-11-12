
from crewai import Task


def create_tasks(
    planner_agent,
    researcher_agent,
    executor_agent,
    reviewer_agent,
    user_task
):

    # TASK 1: PLANNING

    planning_task = Task(
        description=f"""
        Understand the following user request:

        {user_task}

        Break this request into smaller steps.

        Identify the tools and resources required.
        Provide a logical execution plan.
        """,

        expected_output="""
        A numbered execution plan with clear steps,
        required resources and expected deliverables.
        """,

        agent=planner_agent
    )


    # TASK 2: RESEARCH

    research_task = Task(
    description="""
    Research the following request:

    {user_task}

    Use the Web Search Tool only when necessary.

    Find relevant information from the search results.
    Summarize the important findings clearly.

    Do not repeat the same search unnecessarily.
    Do not invent facts or sources.
    """,
    expected_output="""
    A concise research summary containing:
    - Important findings
    - Company names, if relevant
    - Supporting source URLs
    """,
    agent=researcher_agent,
    context=[planning_task]
)


    # TASK 3: EXECUTION

    execution_task = Task(
        description=f"""
        Execute the user's request:

        {user_task}

        Use the planning task and research task as context.

        Perform the necessary calculations or file operations.

        If the user requests a report, create a Markdown
        report and a PDF report when appropriate.

        Do not claim an operation succeeded unless the
        corresponding tool confirms success.
        """,

        expected_output="""
        A detailed execution summary describing:
        - Actions performed
        - Calculations completed
        - Files created
        - File locations
        - Any incomplete operations
        """,

        agent=executor_agent,

        context=[planning_task, research_task]
    )


    # TASK 4: REVIEW

    review_task = Task(
        description=f"""
        Review the completed work for the user request:

        {user_task}

        Examine the plan, research and execution results.

        Identify missing requirements and inaccuracies.

        Provide the final result in a professional format.
        """,

        expected_output="""
        A final reviewed response explaining:
        - What was requested
        - What was completed
        - Results and findings
        - Generated files
        - Any limitations or incomplete work
        """,

        agent=reviewer_agent,

        context=[planning_task, research_task, execution_task]
    )

    return [
        planning_task,
        research_task,
        execution_task,
        review_task
    ]
