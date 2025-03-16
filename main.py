# import necessary modules and libraries
import streamlit as st
import random
import json
import datetime
import time
import base64

# Create required states
if "first_name" not in st.session_state:
    st.session_state.first_name = ""
if "last_name" not in st.session_state:
    st.session_state.last_name = ""
if "approved" not in st.session_state:
    st.session_state.approved = False
if "validation_message" not in st.session_state:
    st.session_state.validation_message = ""
if "assignment_message" not in st.session_state:
    st.session_state.assignment_message = ""
if "remark" not in st.session_state:
    st.session_state.remark = ""
if "remark_message" not in st.session_state:
    st.session_state.remark_message = ""
if "assigned" not in st.session_state:
    st.session_state.assigned = False
if "button_disabled" not in st.session_state:
    st.session_state.button_disabled = False
if "button_disabled_2" not in st.session_state:
    st.session_state.button_disabled_2 = False

# Read and store current details status
with open(file="details.json", mode="r") as details_file:
    details = json.load(details_file)
approved_names = details["approved_names"]
done = details["done"]


def get_info_by_surname(last_name):

    """
    Retrieves course assignment information for a given surname from a JSON file.
    Args:
        last_name (str): The surname to search for in the course assignment data.
    Returns:
        dict: A dictionary containing the course assignment details if found,
              otherwise an empty dictionary.
    """

    try:
        with open(file="course_assignment.json", mode="r") as file:
            ass = json.load(file)
    except FileNotFoundError:
        return {}
    else:
        for i in ass:
            if last_name in ass[i]["anchor_name"]:
                return ass[i]
    return {}


def validate():
    """
    Validates the user's surname against approved and assigned lists, updating the session state accordingly.

    Retrieves the last name from Streamlit's session state, checks if the user has already been assigned
    a course, is not approved, or is eligible to proceed. Updates `st.session_state` with the appropriate
    validation message and approval status.

    Side Effects:
        - Updates `st.session_state.validation_message` with a formatted message.
        - Updates `st.session_state.approved` as True or False.

    """

    oruko_idile = st.session_state.last_name.lower()
    print("in func now", oruko_idile)
    if oruko_idile in done:
        st.session_state.validation_message = (f"### **REST!**\n✅ You have been assigned a course already | "
                                               f"📚 Your course is: **_{get_info_by_surname(oruko_idile).get("course_name")}_**")
        st.session_state.approved = False
    elif oruko_idile not in approved_names:
        st.session_state.validation_message = ("### 🚫 **Not approved!**\n"
                                               "Ensure your surname is correct or contact the app creator.")
        st.session_state.approved = False
    else:
        st.session_state.approved = True
        st.session_state.validation_message = "### ✅ **You are approved**\nGenerate your course!"


def assign():
    """
    Assigns a course to the user based on their first and last name, updates relevant files,
    and modifies the session state accordingly.

    This function:
        - Reads the available courses from `courses.json`.
        - Generates a deterministic seed from the user's name to select a course.
        - Removes the assigned course from the available list.
        - Logs assignment details (name, course, timestamp, etc.) in `course_assignment.json`.
        - Updates `approved_names` and `done` lists in `details.json`.
        - Displays a confirmation message in the session state.

    Side Effects:
        - Updates and modifies JSON files (`courses.json`, `course_assignment.json`, `details.json`).
        - Updates `st.session_state.assignment_message` with the assigned course details.
        - Updates `st.session_state.assigned` to `True`.
        - Uses `st.spinner` to indicate progress.
        - Uses `time.sleep(1)` for a brief delay.
    """

    with st.spinner("Generating...", show_time=True):
        time.sleep(1)
        firstname = st.session_state.first_name
        surname = st.session_state.last_name

        with open(file="courses.json", mode="r") as file:
             course_data = json.load(file)["course_list"]
        seed = firstname[:int(len(firstname)/2)] + "_and_" + surname[::2]
        random.seed(seed)
        selection = random.choice(course_data)
        course_data.remove(selection)
        instant_time = datetime.datetime.now()
        position = 5 - len(course_data)
        assignment_data = {
            position: {
                "anchor_name": f"{surname} {firstname}",
                "course_name": selection,
                "seed": seed,
                "time": instant_time.strftime("%H:%M:%S, %A, %B %d, %Y."),
                "remark": "Bro's too lazy to leave a remark!",
                "position": 1+position,
            }
        }
        try:
            with open(file="course_assignment.json", mode="r") as file:
                ass = json.load(file)
        except FileNotFoundError:
            with open(file="course_assignment.json", mode="w") as file:
                json.dump(assignment_data, file, indent=4)
        except json.decoder.JSONDecodeError:
            with open(file="course_assignment.json", mode="w") as file:
                json.dump(assignment_data, file, indent=4)
        else:
            ass.update(assignment_data)
            with open(file="course_assignment.json", mode="w") as file:
                json.dump(ass, file, indent=4)

        with open(file="courses.json", mode="w") as file:
            json.dump({"course_list":course_data}, file, indent=4)

        approved_names.remove(surname)
        done.append(surname)
        new_details = {"approved_names": approved_names, "done": done}
        with open(file="details.json", mode="w") as file:
            json.dump(new_details, file, indent=4)
        time.sleep(1)

    st.session_state.assignment_message = (f"### **🎉Congratulations {surname.title()}!!🎉**\n🥳Course generated successfully | "
                                           f"📚 Your newly generated course is: **_{selection}_**")
    st.session_state.assigned = True
    st.session_state.button_disabled = True
    print("done")


def add_remark():
    """
    Updates the remark for a specific course assignment in `course_assignment.json`.

    This function:
        - Retrieves the course assignment details for the user with the surname "qwerty".
        - Reads `course_assignment.json` and updates the corresponding remark.
        - Saves the updated data back to `course_assignment.json`.
        - Updates `st.session_state.remark_message` to confirm the remark was saved.

    Side Effects:
        - Modifies `course_assignment.json` by updating the remark for the user's course assignment.
        - Updates `st.session_state.remark_message` to notify the user.
        - Prints the current assignment data for debugging.

    Exception Handling:
        - If `course_assignment.json` is not found, the function does nothing.
    """

    info = get_info_by_surname(st.session_state.last_name)
    try:
        with open("course_assignment.json", mode="r") as a_file:
            data = json.load(a_file)
            print(data)
    except FileNotFoundError:
        pass
    else:
        try:
            data[str(info.get("position") - 1)]["remark"] = st.session_state.remark
        except KeyError:
            pass
        else:
            with open("course_assignment.json", mode="w") as a_file:
                json.dump(data, a_file, indent=4)
    st.session_state.remark_message = "Remark saved successfully"
    st.session_state.button_disabled_2 = True


# Display welcome message
welcome_text = """## Course assigner
Welcome to this beautiful application created by the most handsome man in the world, this app was created for a group of
 study buddies, They need to study ahead of the semester so the decided to split the course among themselves for an 
 optimal result. The anchor of each course would master it and teach it to the others, instead of each person mastering 
 it on their own,  smart idea right?

If this was sent to you it means you are a part of the group and you can go ahead to get your course, and if you just 
stumbled on this you won't be able to proceed but you are welcome to click buttons by the right.🤗.)"""
st.markdown(welcome_text)

# Create name input fields and submit button
col1, col2 = st.columns(2)
with col1:
    st.session_state.first_name = st.text_input(label="Firstname", placeholder="Please input your firstname").strip()
with col2:
   st.session_state.last_name = st.text_input(label="Lastname", placeholder="Please input your surname").strip()
st.button(label="Submit for validation", on_click=validate)

# Display result of validation test
st.markdown(st.session_state.validation_message)

# Create button to assign a course upon approval
if st.session_state.approved:
    st.button(label="Generate course", disabled=st.session_state.button_disabled, on_click=assign)

if st.session_state.assigned:
    # Display success message  and remark option upon successful assignment
    st.success(st.session_state.assignment_message)
    st.session_state.remark = st.text_input(label="Leave a remark!", placeholder="What do you feel? What's on your mind?")
    st.button(label="Save remark", disabled=st.session_state.button_disabled_2, on_click=add_remark)
if st.session_state.remark_message != "":
    st.info(st.session_state.remark_message, icon="ℹ️")

# Custom HTML & CSS to position buttons
st.markdown(
    """
    <style>
        .corner-button {
            position: fixed;
            top: 60px;
            right: 20px;
            background-color: #0e1117;
            color: white;
            padding: 10px 10px;
            border: 0.5px solid #ffffff;  /* Thin outline */
            cursor: pointer;
            font-size: 16px;
            border-radius: 5px;
        }
        .corner-button:hover {
            background-color: #ffffff;
            color: #0e1117;
            font-weight: bold;
        }
        /* Positioning each button dynamically */
        .corner-buttons a:nth-child(1) button { top: 20px; left: 20px; }  /* Top-left */
        .corner-buttons a:nth-child(2) button { top: 20px; right: 20px; } /* Top-right */
        .corner-buttons a:nth-child(3) button { bottom: 20px; left: 20px; } /* Bottom-left */
        .corner-buttons a:nth-child(4) button { bottom: 20px; right: 20px; } /* Bottom-right */
    </style>
    <a href="https://www.linkedin.com/in/ebi-emmanuel/" target="_blank">
        <button class="corner-button">🔵Linkedin</button>
    </a>
    <a href="https://medium.com/@ebifredrick07" target="_blank">
        <button style="top: 120px;" class="corner-button">✍️Medium</button>
    </a>
    <a href="https://github.com/Manuel-7tin" target="_blank">
        <button style="top: 180px;" class="corner-button">🐙Github</button>
    </a>
    <a href="https://www.imdb.com/title/tt2560140/" target="_blank">
        <button style="top: 240px;" class="corner-button">⚔️AOT</button>
    </a>
    """,
    unsafe_allow_html=True
)
