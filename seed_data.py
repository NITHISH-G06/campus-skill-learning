"""
Sri Eshwar College of Engineering - Campus Skill Exchange
Sample Data Seeder

Seeds the SQLite database with realistic fictional data reflecting peer tutoring
across multiple academic engineering departments at Sri Eshwar College of Engineering.
"""

from datetime import datetime, timedelta
import random
from database import init_db, get_db_connection
from auth import register_user
from db_ops import (
    create_listing,
    create_session_request,
    update_request_status,
    create_async_question,
    create_async_answer,
    create_review,
    close_question,
)
from config import CAMPUS_MEETING_SPOTS, STATUS_ACCEPTED, STATUS_COMPLETED, STATUS_PENDING, STATUS_DECLINED

def seed_sample_data(reset_existing: bool = False) -> None:
    """Populate database with sample college data safely without erasing registered users."""
    init_db()

    if reset_existing:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM commission_records")
            conn.execute("DELETE FROM reviews")
            conn.execute("DELETE FROM async_answers")
            conn.execute("DELETE FROM async_questions")
            conn.execute("DELETE FROM session_requests")
            conn.execute("DELETE FROM listings")
            conn.commit()

    # 1. Register or find Admin
    with get_db_connection() as conn:
        admin_row = conn.execute("SELECT id FROM users WHERE email = 'admin@sece.ac.in'").fetchone()
    if not admin_row:
        register_user(
            name="Dean of Academics (Admin)",
            email="admin@sece.ac.in",
            password="admin123",
            department="Computer Science & Engineering (CSE)",
            year_of_study="Faculty / Admin",
            bio="Academic coordinator overseeing peer tutoring initiatives, quality mentorship, and campus skill exchange analytics.",
            learning_interests="Curriculum Analytics, Student Mentorship, Engineering Pedagogy",
            is_admin=True,
        )

    # 2. Register or find sample students
    sample_students = [
        {
            "name": "Kavya Sundaram",
            "email": "kavya.cse@sece.ac.in",
            "password": "student123",
            "department": "Computer Science & Engineering (CSE)",
            "year_of_study": "3rd Year (Junior)",
            "bio": "Competitive programmer (LeetCode 1800+), passionate about teaching Data Structures, C++, and Python.",
            "learning_interests": "Cloud Computing, Distributed Systems, System Design",
        },
        {
            "name": "Arun Kumar M",
            "email": "arun.aids@sece.ac.in",
            "password": "student123",
            "department": "Artificial Intelligence & Data Science (AI & DS)",
            "year_of_study": "4th Year (Senior)",
            "bio": "Deep Learning enthusiast. Winner of Smart India Hackathon. Love demystifying neural nets and math.",
            "learning_interests": "Large Language Models, MLOps, Computer Vision",
        },
        {
            "name": "Priyanka Ravi",
            "email": "priyanka.ece@sece.ac.in",
            "password": "student123",
            "department": "Electronics & Communication Engineering (ECE)",
            "year_of_study": "3rd Year (Junior)",
            "bio": "Embedded systems nerd working with ESP32 and ARM Cortex. Can help with digital logic and microcontrollers.",
            "learning_interests": "IoT Protocols, PCB Design, Robotics",
        },
        {
            "name": "Dinesh Chandran",
            "email": "dinesh.it@sece.ac.in",
            "password": "student123",
            "department": "Information Technology (IT)",
            "year_of_study": "2nd Year (Sophomore)",
            "bio": "Full-stack developer building with React, Node.js, and SQL. Happy to help freshers build their first web app.",
            "learning_interests": "Next.js, TailwindCSS, Docker, DevOps",
        },
        {
            "name": "Sneha Venkatesh",
            "email": "sneha.mech@sece.ac.in",
            "password": "student123",
            "department": "Mechanical Engineering (MECH)",
            "year_of_study": "4th Year (Senior)",
            "bio": "SolidWorks and AutoCAD specialist. Interested in EV design and finite element analysis.",
            "learning_interests": "MATLAB, CFD Simulation, Python for Engineers",
        },
        {
            "name": "Rahul Ramanathan",
            "email": "rahul.eee@sece.ac.in",
            "password": "student123",
            "department": "Electrical & Electronics Engineering (EEE)",
            "year_of_study": "2nd Year (Sophomore)",
            "bio": "Enthusiastic about power electronics and circuit simulation. Currently preparing for gate and placements.",
            "learning_interests": "Embedded C, Control Systems, Power Systems",
        },
        {
            "name": "Ananya Sharma",
            "email": "ananya.civil@sece.ac.in",
            "password": "student123",
            "department": "Civil Engineering",
            "year_of_study": "3rd Year (Junior)",
            "bio": "Certified in Revit Architecture and AutoCAD 2D/3D. Passionate about sustainable structural design.",
            "learning_interests": "BIM Modeling, Project Management, Structural Analysis",
        },
        {
            "name": "Harish Balaji",
            "email": "harish.cse@sece.ac.in",
            "password": "student123",
            "department": "Computer Science & Engineering (CSE)",
            "year_of_study": "4th Year (Senior)",
            "bio": "DevOps practitioner and cloud enthusiast (AWS Solutions Architect Certified). Docker, Kubernetes & CI/CD lover.",
            "learning_interests": "Site Reliability Engineering, Terraform, Microservices",
        },
        {
            "name": "Meera Krishnan",
            "email": "meera.aids@sece.ac.in",
            "password": "student123",
            "department": "Artificial Intelligence & Data Science (AI & DS)",
            "year_of_study": "3rd Year (Junior)",
            "bio": "Computer Vision researcher. Published paper on automated defect detection using YOLO and OpenCV.",
            "learning_interests": "Generative AI, Diffusion Models, PyTorch",
        },
    ]

    user_ids = {}
    with get_db_connection() as conn:
        for st in sample_students:
            cur = conn.execute("SELECT id FROM users WHERE email = ?", (st["email"].strip().lower(),))
            row = cur.fetchone()
            if row:
                user_ids[st["email"]] = row["id"]
            else:
                success, msg, uid = register_user(
                    name=st["name"],
                    email=st["email"],
                    password=st["password"],
                    department=st["department"],
                    year_of_study=st["year_of_study"],
                    bio=st["bio"],
                    learning_interests=st["learning_interests"],
                )
                if success and uid:
                    user_ids[st["email"]] = uid

    # 3. Create Tutor Listings if none exist
    with get_db_connection() as conn:
        cur = conn.execute("SELECT COUNT(id) as count FROM listings")
        listing_count = cur.fetchone()["count"]

    if listing_count == 0 or reset_existing:
        listings_data = [
            {
                "email": "kavya.cse@sece.ac.in",
                "subject": "Data Structures & Algorithms",
                "description": "Master Trees, Graphs, Dynamic Programming, and time-complexity optimization for technical interview rounds.",
                "is_paid": False,
                "price": 0.0,
                "modes": ["ONLINE", "ON_CAMPUS", "ASYNCHRONOUS"],
                "availability": "Mon, Wed, Fri: 4:30 PM - 6:30 PM",
            },
            {
                "email": "kavya.cse@sece.ac.in",
                "subject": "Python Programming",
                "description": "From fundamentals to Object-Oriented design, NumPy, and standard libraries. Practical coding exercises & lab exam prep.",
                "is_paid": True,
                "price": 150.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Tue, Thu: 5:00 PM - 7:00 PM; Sat: 10:00 AM - 12:00 PM",
            },
            {
                "email": "arun.aids@sece.ac.in",
                "subject": "Machine Learning & AI",
                "description": "Supervised/unsupervised algorithms, scikit-learn, PyTorch fundamentals, model evaluation, and practical math intuition.",
                "is_paid": True,
                "price": 200.0,
                "modes": ["ONLINE", "ON_CAMPUS", "ASYNCHRONOUS"],
                "availability": "Wed, Sat: 3:00 PM - 6:00 PM",
            },
            {
                "email": "arun.aids@sece.ac.in",
                "subject": "Deep Learning & Neural Networks",
                "description": "Backpropagation, CNNs for vision, RNNs/Transformers, hyperparameter tuning, and training architectures on Google Colab.",
                "is_paid": True,
                "price": 220.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Sun: 10:00 AM - 1:00 PM",
            },
            {
                "email": "priyanka.ece@sece.ac.in",
                "subject": "Microcontrollers & Embedded C",
                "description": "ESP32, Arduino, timer interrupts, ADC, and I2C/SPI sensor interfacing with live hardware debugging sessions.",
                "is_paid": False,
                "price": 0.0,
                "modes": ["ON_CAMPUS", "ASYNCHRONOUS"],
                "availability": "Mon, Thu: 4:00 PM - 6:00 PM",
            },
            {
                "email": "dinesh.it@sece.ac.in",
                "subject": "Web Development (HTML/CSS/JS/React)",
                "description": "Frontend fundamentals, building responsive web apps with React, TailwindCSS, DOM manipulation, and state management.",
                "is_paid": True,
                "price": 100.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Daily: 5:30 PM - 7:30 PM",
            },
            {
                "email": "harish.cse@sece.ac.in",
                "subject": "Cloud Computing & DevOps",
                "description": "Docker containerization, GitHub Actions CI/CD pipelines, AWS EC2 & S3 deployment, and Linux command-line mastery.",
                "is_paid": True,
                "price": 180.0,
                "modes": ["ONLINE", "ASYNCHRONOUS"],
                "availability": "Sat, Sun: 2:00 PM - 5:00 PM",
            },
            {
                "email": "sneha.mech@sece.ac.in",
                "subject": "Engineering Mathematics & Statistics",
                "description": "Linear algebra, differential equations, Fourier transforms, probability distributions, and engineering problem solving.",
                "is_paid": False,
                "price": 0.0,
                "modes": ["ONLINE", "ON_CAMPUS", "ASYNCHRONOUS"],
                "availability": "Sat, Sun: 10:00 AM - 1:00 PM",
            },
            {
                "email": "ananya.civil@sece.ac.in",
                "subject": "Structural Analysis & AutoCAD",
                "description": "Drafting 2D floor plans, 3D structural modeling, beam stress calculations, and bending moment diagrams simplified.",
                "is_paid": False,
                "price": 0.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Tue, Fri: 4:30 PM - 6:30 PM",
            },
            {
                "email": "meera.aids@sece.ac.in",
                "subject": "Computer Vision & OpenCV",
                "description": "Image filtering, edge detection, object detection with YOLO, and real-time webcam video processing pipelines.",
                "is_paid": True,
                "price": 160.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Mon, Wed: 5:00 PM - 7:00 PM",
            },
            {
                "email": "rahul.eee@sece.ac.in",
                "subject": "Circuit Theory & MATLAB Simulation",
                "description": "Kirchhoff's laws, nodal analysis, AC/DC circuit analysis, and Simulink circuit simulations for lab coursework.",
                "is_paid": False,
                "price": 0.0,
                "modes": ["ON_CAMPUS"],
                "availability": "Wed, Fri: 4:00 PM - 6:00 PM",
            },
            {
                "email": "kavya.cse@sece.ac.in",
                "subject": "Aptitude & Placement Interview Prep",
                "description": "Quantitative aptitude shortcuts, logical reasoning, mock technical interviews, and resume structuring for campus placements.",
                "is_paid": True,
                "price": 120.0,
                "modes": ["ONLINE", "ON_CAMPUS"],
                "availability": "Sat: 4:00 PM - 7:00 PM",
            },
        ]

        listing_map = {}
        for l in listings_data:
            t_id = user_ids.get(l["email"])
            if t_id:
                s, m, lid = create_listing(
                    tutor_id=t_id,
                    subject=l["subject"],
                    description=l["description"],
                    is_paid=l["is_paid"],
                    price=l["price"],
                    modes=l["modes"],
                    availability=l["availability"],
                )
                if s and lid:
                    listing_map[(l["email"], l["subject"])] = lid

        print(f"Created {len(listing_map)} tutor listings.")

    # 4. Create Session Requests if none exist
    with get_db_connection() as conn:
        cur = conn.execute("SELECT COUNT(id) as count FROM session_requests")
        req_count = cur.fetchone()["count"]

    if req_count == 0 or reset_existing:
        today = datetime.now().date()
        kavya_id = user_ids.get("kavya.cse@sece.ac.in")
        arun_id = user_ids.get("arun.aids@sece.ac.in")
        dinesh_id = user_ids.get("dinesh.it@sece.ac.in")
        rahul_id = user_ids.get("rahul.eee@sece.ac.in")
        priyanka_id = user_ids.get("priyanka.ece@sece.ac.in")
        harish_id = user_ids.get("harish.cse@sece.ac.in")
        meera_id = user_ids.get("meera.aids@sece.ac.in")
        ananya_id = user_ids.get("ananya.civil@sece.ac.in")
        sneha_id = user_ids.get("sneha.mech@sece.ac.in")

        with get_db_connection() as conn:
            # Helper to get listing ID by subject and tutor
            def get_lid(tutor_id, subject):
                row = conn.execute("SELECT id FROM listings WHERE tutor_id = ? AND subject = ?", (tutor_id, subject)).fetchone()
                return row["id"] if row else None

        if kavya_id and rahul_id:
            # Session 1: Completed Online session
            date1 = (today - timedelta(days=6)).strftime("%Y-%m-%d")
            s, m, req1 = create_session_request(
                listing_id=None,
                learner_id=rahul_id,
                tutor_id=kavya_id,
                mode="ONLINE",
                session_date=date1,
                session_time="17:00",
                notes="Need help preparing for Python lab assessment on dictionaries and list comprehensions.",
                price=150.0,
            )
            if s and req1:
                update_request_status(
                    req1, kavya_id, STATUS_ACCEPTED,
                    tutor_note="Accepted! Bring your practice questions.",
                    meet_link="[DEMO MODE] https://meet.google.com/sec-dsa-kvy",
                    is_demo_link=True,
                )
                update_request_status(req1, kavya_id, STATUS_COMPLETED)
                create_review(req1, rahul_id, kavya_id, 5, "Kavya is an amazing tutor! Cleared all my recursion and dictionary doubts patiently.")

        if arun_id and dinesh_id:
            # Session 2: Completed On-Campus session
            date2 = (today - timedelta(days=4)).strftime("%Y-%m-%d")
            s, m, req2 = create_session_request(
                listing_id=None,
                learner_id=dinesh_id,
                tutor_id=arun_id,
                mode="ON_CAMPUS",
                session_date=date2,
                session_time="15:30",
                meeting_spot="Central Library - 2nd Floor Discussion Zone",
                notes="Discussing gradient descent convergence and loss curve debugging.",
                price=200.0,
            )
            if s and req2:
                update_request_status(req2, arun_id, STATUS_ACCEPTED, tutor_note="See you at table 4 near the whiteboard.")
                update_request_status(req2, dinesh_id, STATUS_COMPLETED)
                create_review(req2, dinesh_id, arun_id, 5, "Incredible insights into backprop and loss curves. Highly recommend!")

        if priyanka_id and rahul_id:
            # Session 3: Completed On-Campus session
            date3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
            s, m, req3 = create_session_request(
                listing_id=None,
                learner_id=rahul_id,
                tutor_id=priyanka_id,
                mode="ON_CAMPUS",
                session_date=date3,
                session_time="16:00",
                meeting_spot="ECE Block - Embedded Systems Lab Discussion Area",
                notes="Setting up GPIO interrupts and timer triggers on ESP32 development board.",
                price=0.0,
            )
            if s and req3:
                update_request_status(req3, priyanka_id, STATUS_ACCEPTED, tutor_note="Bring your ESP32 board and USB-C cable.")
                update_request_status(req3, rahul_id, STATUS_COMPLETED)
                create_review(req3, rahul_id, priyanka_id, 5, "Hands-on and very practical. Resolved our hardware glitch in 30 mins.")

        if harish_id and meera_id:
            # Session 4: Completed Online session
            date4 = (today - timedelta(days=2)).strftime("%Y-%m-%d")
            s, m, req4 = create_session_request(
                listing_id=None,
                learner_id=meera_id,
                tutor_id=harish_id,
                mode="ONLINE",
                session_date=date4,
                session_time="16:30",
                notes="Dockerizing a FastAPI and PyTorch image for cloud deployment.",
                price=180.0,
            )
            if s and req4:
                update_request_status(
                    req4, harish_id, STATUS_ACCEPTED,
                    tutor_note="Accepted! We will build a multi-stage Dockerfile live.",
                    meet_link="[DEMO MODE] https://meet.google.com/sec-ops-hrsh",
                    is_demo_link=True,
                )
                update_request_status(req4, harish_id, STATUS_COMPLETED)
                create_review(req4, meera_id, harish_id, 5, "Harish explained multi-stage builds and layer caching brilliantly! Saved 1.5 GB in my Docker image.")

        if sneha_id and ananya_id:
            # Session 5: Completed session
            date5 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            s, m, req5 = create_session_request(
                listing_id=None,
                learner_id=ananya_id,
                tutor_id=sneha_id,
                mode="ON_CAMPUS",
                session_date=date5,
                session_time="11:00",
                meeting_spot="Central Library - Digital Resource Center",
                notes="Eigenvalues, Eigenvectors, and Matrix diagonalization for structural loads.",
                price=0.0,
            )
            if s and req5:
                update_request_status(req5, sneha_id, STATUS_ACCEPTED, tutor_note="See you in the library.")
                update_request_status(req5, ananya_id, STATUS_COMPLETED)
                create_review(req5, ananya_id, sneha_id, 4, "Sneha made linear algebra so much simpler to understand.")

        if kavya_id and dinesh_id:
            # Session 6: Accepted upcoming Online session
            date6 = (today + timedelta(days=2)).strftime("%Y-%m-%d")
            s, m, req6 = create_session_request(
                listing_id=None,
                learner_id=dinesh_id,
                tutor_id=kavya_id,
                mode="ONLINE",
                session_date=date6,
                session_time="17:00",
                notes="Trie implementation and graph BFS traversals.",
                price=0.0,
            )
            if s and req6:
                update_request_status(
                    req6, kavya_id, STATUS_ACCEPTED,
                    tutor_note="Accepted! We will code live on Google Meet.",
                    meet_link="[DEMO MODE] https://meet.google.com/sec-alg-dsa",
                    is_demo_link=True,
                )

        if dinesh_id and rahul_id:
            # Session 7: Accepted upcoming On-Campus session
            date7 = (today + timedelta(days=3)).strftime("%Y-%m-%d")
            s, m, req7 = create_session_request(
                listing_id=None,
                learner_id=rahul_id,
                tutor_id=dinesh_id,
                mode="ON_CAMPUS",
                session_date=date7,
                session_time="17:30",
                meeting_spot="SECE Innovation & Incubation Center - Brainstorm Pod",
                notes="Connecting Streamlit UI to a REST API backend.",
                price=100.0,
            )
            if s and req7:
                update_request_status(req7, dinesh_id, STATUS_ACCEPTED, tutor_note="Confirmed! Bring your laptop with Node.js installed.")

        if arun_id and kavya_id:
            # Session 8: Pending Request
            date8 = (today + timedelta(days=4)).strftime("%Y-%m-%d")
            create_session_request(
                listing_id=None,
                learner_id=kavya_id,
                tutor_id=arun_id,
                mode="ONLINE",
                session_date=date8,
                session_time="11:00",
                notes="Want to understand attention mechanisms and self-attention in Transformers.",
                price=220.0,
            )

    # 5. Create Asynchronous Questions and Answers if none exist
    with get_db_connection() as conn:
        cur = conn.execute("SELECT COUNT(id) as count FROM async_questions")
        q_count = cur.fetchone()["count"]

    if q_count == 0 or reset_existing:
        rahul_id = user_ids.get("rahul.eee@sece.ac.in")
        kavya_id = user_ids.get("kavya.cse@sece.ac.in")
        dinesh_id = user_ids.get("dinesh.it@sece.ac.in")
        arun_id = user_ids.get("arun.aids@sece.ac.in")
        priyanka_id = user_ids.get("priyanka.ece@sece.ac.in")
        ananya_id = user_ids.get("ananya.civil@sece.ac.in")
        harish_id = user_ids.get("harish.cse@sece.ac.in")

        if rahul_id and kavya_id:
            s, m, q1 = create_async_question(
                learner_id=rahul_id,
                subject="Python Programming",
                title="Why does mutable default argument behave unexpectedly in Python functions?",
                question_text="I defined `def append_item(val, my_list=[]): my_list.append(val); return my_list`. When I call it multiple times, the list accumulates items across calls! Why does this happen and what is the idiomatic fix?",
                code_snippet="def add_item(val, container=[]):\n    container.append(val)\n    return container\n\nprint(add_item(1)) # [1]\nprint(add_item(2)) # [1, 2] -- expected [2]!",
            )
            if s and q1:
                create_async_answer(
                    question_id=q1,
                    tutor_id=kavya_id,
                    answer_text="In Python, default arguments are evaluated only once at the time of function definition, not on each invocation! To fix this, use `None` as the default sentinel value:\n\n```python\ndef add_item(val, container=None):\n    if container is None:\n        container = []\n    container.append(val)\n    return container\n```",
                )

        if dinesh_id and arun_id:
            s, m, q2 = create_async_question(
                learner_id=dinesh_id,
                subject="Machine Learning & AI",
                title="Difference between L1 (Lasso) and L2 (Ridge) Regularization in simple terms?",
                question_text="Can someone explain the geometrical intuition of why L1 regularization produces sparse weights (forces some coefficients to exact zero) while L2 only shrinks them?",
            )
            if s and q2:
                create_async_answer(
                    question_id=q2,
                    tutor_id=arun_id,
                    answer_text="Geometrically, L1 has sharp diamond-shaped constraint boundaries whose corners intersect coordinate axes directly, driving coefficients to zero. L2 has circular/hyperspherical constraints where the minimum loss contour usually touches smooth arcs instead of axes.",
                )

        if priyanka_id and kavya_id:
            s, m, q3 = create_async_question(
                learner_id=priyanka_id,
                subject="Data Structures & Algorithms",
                title="Best approach to detect a cycle in a Directed Graph vs Undirected Graph?",
                question_text="For undirected graphs we can use simple BFS/DFS with a parent pointer or Disjoint Set Union (DSU). Why doesn't simple parent checking work for directed graphs, and what is the standard algorithm?",
            )
            if s and q3:
                create_async_answer(
                    question_id=q3,
                    tutor_id=kavya_id,
                    answer_text="In directed graphs, an edge pointing to an already visited vertex is not necessarily a cycle (it could be a cross-edge or forward-edge). You must check if the vertex is in the current recursion stack (ancestor) using 3-color DFS (WHITE=unvisited, GRAY=in-progress, BLACK=done) or Kahn's algorithm (topological sort with in-degrees).",
                )

        if ananya_id and harish_id:
            s, m, q4 = create_async_question(
                learner_id=ananya_id,
                subject="Cloud Computing & DevOps",
                title="What is the difference between a Docker Image and a Docker Container?",
                question_text="Can someone explain the relationship between a Dockerfile, an Image, and a Container using a simple engineering analogy?",
            )
            if s and q4:
                create_async_answer(
                    question_id=q4,
                    tutor_id=harish_id,
                    answer_text="A great analogy is Object-Oriented Programming or Civil Engineering blueprints:\n\n- **Dockerfile**: The recipe or architectural blueprint.\n- **Image**: The compiled class or prefabricated mold (read-only snapshot of filesystem + dependencies).\n- **Container**: A running instance of that class or the actual constructed building (a live, isolated process with its own writable layer).",
                )

        if rahul_id and priyanka_id:
            s, m, q5 = create_async_question(
                learner_id=rahul_id,
                subject="Microcontrollers & Embedded C",
                title="Why does button press trigger multiple interrupts on ESP32?",
                question_text="When I attach a GPIO falling interrupt to a tactile push button on ESP32, my ISR fires 5-10 times for a single press. How to implement clean software debouncing in Embedded C?",
            )
            if s and q5:
                create_async_answer(
                    question_id=q5,
                    tutor_id=priyanka_id,
                    answer_text="Mechanical switches have metal contacts that bounce for 5-20 milliseconds before settling. In your ISR, record `millis()` and ignore triggers that occur within 50ms of the previous timestamp:\n\n```c\nvolatile unsigned long last_interrupt_time = 0;\n\nvoid IRAM_ATTR button_isr() {\n    unsigned long interrupt_time = millis();\n    if (interrupt_time - last_interrupt_time > 50) {\n        button_pressed = true;\n    }\n    last_interrupt_time = interrupt_time;\n}\n```",
                )

    print("Sample data populated successfully!")

if __name__ == "__main__":
    seed_sample_data(reset_existing=True)
