
import streamlit as st
from pathlib import Path

from crew import execute_task

from database import (
    initialize_database,
    save_task,
    get_task_history,
    get_task_result
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Task Execution Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize database
initialize_database()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🤖 Task Execution Agent")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "New Task",
        "Task History"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Powered by CrewAI + Ollama + Qwen"
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.title("🤖 Task Execution Agent")

    st.write(
        "An autonomous AI system that plans, "
        "researches and executes user instructions."
    )

    history = get_task_history()

    total_tasks = len(history)

    completed_tasks = sum(
        1 for record in history
        if record[2] == "Completed"
    )

    failed_tasks = sum(
        1 for record in history
        if record[2] == "Failed"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tasks", total_tasks)

    col2.metric("Completed Tasks", completed_tasks)

    col3.metric("Failed Tasks", failed_tasks)

    st.divider()

    st.subheader("Recent Tasks")

    if history:

        for record in history[:5]:

            with st.container(border=True):

                st.write(f"**Task #{record[0]}**")

                st.write(record[1])

                st.caption(
                    f"Status: {record[2]} | Date: {record[3]}"
                )

    else:

        st.info("No tasks executed yet.")


# --------------------------------------------------
# NEW TASK
# --------------------------------------------------

elif page == "New Task":

    st.title("🚀 Execute a New Task")

    st.write(
        "Describe what you want your AI agents to accomplish."
    )

    user_task = st.text_area(
        "Enter your task",

        placeholder=(
            "Example: Research the top 5 AI companies "
            "in India, compare their technologies and "
            "generate a PDF report."
        ),

        height=150
    )

    if st.button(
        "Execute Task",
        type="primary",
        use_container_width=True
    ):

        if not user_task.strip():

            st.warning("Please enter a task.")

        else:

            with st.spinner(
                "AI agents are planning, researching and executing..."
            ):

                try:

                    result = execute_task(user_task)

                    save_task(
                        user_task,
                        result,
                        "Completed"
                    )

                    st.session_state["last_result"] = result

                    st.session_state["last_task"] = user_task

                    st.success("Task execution completed!")

                except Exception as e:

                    error_message = str(e)

                    save_task(
                        user_task,
                        error_message,
                        "Failed"
                    )

                    st.error(
                        f"Task execution failed: {error_message}"
                    )

    # Display the result outside the button block
    if "last_result" in st.session_state:

        st.divider()

        st.subheader("📋 Execution Result")

        st.markdown(st.session_state["last_result"])

        st.download_button(
            label="Download Result",

            data=st.session_state["last_result"],

            file_name="task_result.md",

            mime="text/markdown"
        )

        # Display generated files
        st.subheader("📁 Generated Files")

        output_dir = Path("outputs")

        if output_dir.exists():

            files = list(output_dir.glob("*"))

            if files:

                for file in files:

                    if file.is_file():

                        st.write(f"📄 {file.name}")

                        if file.suffix.lower() == ".pdf":

                            st.download_button(
                                label=f"Download {file.name}",

                                data=file.read_bytes(),

                                file_name=file.name,

                                mime="application/pdf",

                                key=f"download_{file.name}"
                            )

                        elif file.suffix.lower() in [".md", ".txt"]:

                            st.download_button(
                                label=f"Download {file.name}",

                                data=file.read_bytes(),

                                file_name=file.name,

                                mime="text/plain",

                                key=f"download_{file.name}"
                            )


# --------------------------------------------------
# TASK HISTORY
# --------------------------------------------------

elif page == "Task History":

    st.title("📚 Task History")

    history = get_task_history()

    if history:

        for record in history:

            task_id = record[0]

            with st.expander(
                f"Task #{task_id} - {record[2]} - {record[3]}"
            ):

                st.write("**User Request:**")

                st.write(record[1])

                if st.button(
                    "View Result",
                    key=f"view_{task_id}"
                ):

                    result_data = get_task_result(task_id)

                    if result_data:

                        st.markdown(result_data[1])

    else:

        st.info("No previous tasks found.")
