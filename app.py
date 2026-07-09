import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import urllib.parse
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Campus Portal", page_icon="🏫")

# 2. Safely encode your credentials
username = "thouhid"
password = "db_nriit123"  # Your active password
escaped_password = urllib.parse.quote_plus(password)

MONGO_URI = f"mongodb+srv://thouhid:nriit123@cluster0.1ekinme.mongodb.net/?appName=Cluster0"

# 3. Connection function
@st.cache_resource(show_spinner="Connecting to Database...")
def init_connection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        return client
    except Exception as e:
        return None

client = init_connection()

# 4. Verify connection status visually in the UI
if client is not None:
    try:
        db = client["campus-portal-backend"]
        client.admin.command('ping')
        
        # Define collections
        student_collection = db["students"]
        faculty_collection = db["faculty"]
        course_collection = db["courses"]
        enrollment_collection = db["enrollments"]
        
        st.sidebar.success("📶 Database Connected!")
        
        # ==========================================
        # 5. NAVIGATION & LAYOUT
        # ==========================================
        st.title("🏫 Campus Portal Management System")
        
        form_type = st.sidebar.radio(
            "Navigation", 
            ["Student Registration", "Faculty Registration", "Add New Course", "Student Enrollment"]
        )
        
        # --- Form 1: Student Registration ---
        if form_type == "Student Registration":
            st.header("🎓 Student Details Form")
            with st.form("student_form", clear_on_submit=True):
                student_id = st.text_input("Student ID (e.g., STU101)")
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                department = st.selectbox("Department", ["Computer Science", "Information Technology", "Electronics", "Mechanical"])
                year = st.slider("Current Year", 1, 4, 1)
                
                if st.form_submit_button("Submit Student"):
                    if not student_id or not name or not email:
                        st.error("Please fill out all required fields.")
                    else:
                        student_collection.insert_one({
                            "student_id": student_id, "name": name, "email": email, "department": department, "year": year
                        })
                        st.success(f"🎉 Student {name} added successfully to MongoDB!")

        # --- Form 2: Faculty Registration ---
        elif form_type == "Faculty Registration":
            st.header("👨‍🏫 Faculty Details Form")
            with st.form("faculty_form", clear_on_submit=True):
                faculty_id = st.text_input("Faculty ID (e.g., FAC201)")
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                designation = st.selectbox("Designation", ["Assistant Professor", "Associate Professor", "Professor", "HOD"])
                specialization = st.text_input("Area of Specialization")
                
                if st.form_submit_button("Submit Faculty"):
                    if not faculty_id or not name or not email:
                        st.error("Please fill out all required fields.")
                    else:
                        faculty_collection.insert_one({
                            "faculty_id": faculty_id, "name": name, "email": email, "designation": designation, "specialization": specialization
                        })
                        st.success(f"🎉 Faculty {name} added successfully to MongoDB!")

        # --- Form 3: Add New Course ---
        elif form_type == "Add New Course":
            st.header("📚 Add New Course")
            with st.form("course_form", clear_on_submit=True):
                course_id = st.text_input("Course Code (e.g., CS301)")
                course_name = st.text_input("Course Title (e.g., Database Management Systems)")
                credits = st.number_input("Credits", min_value=1, max_value=5, value=3)
                department = st.selectbox("Offered By Department", ["Computer Science", "Information Technology", "Electronics", "Mechanical"])
                
                if st.form_submit_button("Add Course"):
                    if not course_id or not course_name:
                        st.error("Course Code and Title are required.")
                    else:
                        course_collection.insert_one({
                            "course_id": course_id, "course_name": course_name, "credits": credits, "department": department
                        })
                        st.success(f"🎉 Course '{course_name}' stored successfully!")

        # --- Form 4: Student Enrollment ---
        elif form_type == "Student Enrollment":
            st.header("📝 Student Course Enrollment")
            
            # Fetch existing records dynamically
            students_in_db = list(student_collection.find({}, {"student_id": 1, "name": 1}))
            courses_in_db = list(course_collection.find({}, {"course_id": 1, "course_name": 1}))
            
            if not students_in_db or not courses_in_db:
                st.warning("⚠️ Please ensure you have added at least one Student and one Course before managing enrollments.")
            else:
                student_options = [f"{s['student_id']} - {s['name']}" for s in students_in_db]
                course_options = [f"{c['course_id']} - {c['course_name']}" for c in courses_in_db]
                
                with st.form("enrollment_form", clear_on_submit=True):
                    selected_student = st.selectbox("Select Student", student_options)
                    selected_course = st.selectbox("Select Course to Enroll In", course_options)
                    semester = st.selectbox("Semester", ["Odd Semester", "Even Semester"])
                    
                    if st.form_submit_button("Confirm Enrollment"):
                        stu_id = selected_student.split(" - ")[0]
                        crs_id = selected_course.split(" - ")[0]
                        
                        duplicate_check = enrollment_collection.find_one({"student_id": stu_id, "course_id": crs_id})
                        if duplicate_check:
                            st.error("This student is already enrolled in this course!")
                        else:
                            enrollment_collection.insert_one({
                                "student_id": stu_id,
                                "course_id": crs_id,
                                "semester": semester,
                                "enrollment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.success(f"✅ Successfully enrolled {stu_id} into {crs_id}!")

    except Exception as e:
        st.error(f"❌ Authentication or Network Blocked: {e}")
else:
    st.error("Could not initialize the database driver.")