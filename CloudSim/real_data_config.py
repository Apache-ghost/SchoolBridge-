"""
Real Data Configuration for SchoolBridge Simulation
Contains actual school names, parents, students, and teachers
"""

# Real Schools Configuration
REAL_SCHOOLS = [
    {
        "id": "ict-university",
        "name": "ICT University",
        "region": "us-east",
        "location": "Cameroon Campus - East Region",
        "phone": "+237-677-123-456",
        "email": "admin@ictuniversity.edu.cm"
    },
    {
        "id": "polytech",
        "name": "Polytech Cameroon",
        "region": "us-west", 
        "location": "Cameroon Campus - West Region",
        "phone": "+237-659-987-654",
        "email": "info@polytech.edu.cm"
    },
    {
        "id": "university-yaounde",
        "name": "University of Yaoundé I",
        "region": "eu-central",
        "location": "Yaoundé, Cameroon",
        "phone": "+237-222-234-567",
        "email": "contact@univ-yaounde1.cm"
    }
]

# Real Parents Data
REAL_PARENTS = [
    # ICT University Parents
    {
        "name": "Mr Jean Nkomo", 
        "phone": "677880739",
        "email": "jean.nkomo@gmail.com",
        "school_id": "ict-university",
        "children": ["student_ict_001", "student_ict_002"]
    },
    {
        "name": "Mme Mary Fotso", 
        "phone": "659258713", 
        "email": "mary.fotso@yahoo.fr",
        "school_id": "ict-university",
        "children": ["student_ict_001"]  # Jean's wife, same child
    },
    {
        "name": "Mr Paul Kamdem", 
        "phone": "698123456",
        "email": "paul.kamdem@hotmail.com", 
        "school_id": "ict-university",
        "children": ["student_ict_003"]
    },
    {
        "name": "Mme Claire Mballa", 
        "phone": "677456789",
        "email": "claire.mballa@gmail.com",
        "school_id": "ict-university", 
        "children": ["student_ict_003"]  # Paul's wife
    },
    {
        "name": "Mr Francis Biya", 
        "phone": "659789123",
        "email": "francis.biya@yahoo.com",
        "school_id": "ict-university",
        "children": ["student_ict_004"]
    },

    # Polytech Parents  
    {
        "name": "Dr Ahmed Hassan",
        "phone": "677880739",  # Same as Mr Jean (shows cross-school families)
        "email": "ahmed.hassan@polytech-parent.cm", 
        "school_id": "polytech",
        "children": ["student_poly_001"]
    },
    {
        "name": "Mme Fatima Hassan", 
        "phone": "659258713",  # Same as Mme Mary 
        "email": "fatima.hassan@gmail.com",
        "school_id": "polytech",
        "children": ["student_poly_001"]  # Ahmed's wife
    },
    {
        "name": "Eng. Robert Tchoua", 
        "phone": "698567890",
        "email": "robert.tchoua@engineer.cm",
        "school_id": "polytech", 
        "children": ["student_poly_002"]
    },
    {
        "name": "Mme Sophie Tchoua", 
        "phone": "677345678",
        "email": "sophie.tchoua@yahoo.fr",
        "school_id": "polytech",
        "children": ["student_poly_002"]
    },
    {
        "name": "Mr Daniel Ngono", 
        "phone": "659123987",
        "email": "daniel.ngono@outlook.com",
        "school_id": "polytech",
        "children": ["student_poly_003"]
    },

    # University of Yaoundé Parents
    {
        "name": "Prof. Marie Essomba", 
        "phone": "677999888",
        "email": "marie.essomba@univ.cm",
        "school_id": "university-yaounde", 
        "children": ["student_uy_001"]
    },
    {
        "name": "Dr. Joseph Essomba", 
        "phone": "659888999",
        "email": "joseph.essomba@medical.cm",
        "school_id": "university-yaounde",
        "children": ["student_uy_001"]
    }
]

# Real Students Data
REAL_STUDENTS = [
    # ICT University Students
    {
        "student_id": "student_ict_001",
        "name": "Grace Jean Nkomo", 
        "program": "Computer Science",
        "year": "2nd Year",
        "school_id": "ict-university",
        "parent_names": ["Mr Jean Nkomo", "Mme Mary Fotso"]
    },
    {
        "student_id": "student_ict_002", 
        "name": "David Jean Nkomo",
        "program": "Software Engineering", 
        "year": "1st Year",
        "school_id": "ict-university",
        "parent_names": ["Mr Jean Nkomo"]  # Only father listed
    },
    {
        "student_id": "student_ict_003",
        "name": "Emmanuel Paul Kamdem",
        "program": "Information Systems",
        "year": "3rd Year", 
        "school_id": "ict-university",
        "parent_names": ["Mr Paul Kamdem", "Mme Claire Mballa"]
    },
    {
        "student_id": "student_ict_004",
        "name": "Priscilla Francis Biya", 
        "program": "Cybersecurity",
        "year": "2nd Year",
        "school_id": "ict-university", 
        "parent_names": ["Mr Francis Biya"]
    },

    # Polytech Students
    {
        "student_id": "student_poly_001",
        "name": "Omar Ahmed Hassan",
        "program": "Mechanical Engineering", 
        "year": "4th Year",
        "school_id": "polytech",
        "parent_names": ["Dr Ahmed Hassan", "Mme Fatima Hassan"]
    },
    {
        "student_id": "student_poly_002", 
        "name": "Alice Robert Tchoua",
        "program": "Civil Engineering",
        "year": "3rd Year",
        "school_id": "polytech",
        "parent_names": ["Eng. Robert Tchoua", "Mme Sophie Tchoua"]
    },
    {
        "student_id": "student_poly_003",
        "name": "Samuel Daniel Ngono", 
        "program": "Electrical Engineering",
        "year": "2nd Year", 
        "school_id": "polytech",
        "parent_names": ["Mr Daniel Ngono"]
    },

    # University of Yaoundé Students
    {
        "student_id": "student_uy_001",
        "name": "Stephanie Marie Essomba",
        "program": "Medicine", 
        "year": "5th Year",
        "school_id": "university-yaounde",
        "parent_names": ["Prof. Marie Essomba", "Dr. Joseph Essomba"]
    }
]

# Real Teachers Data
REAL_TEACHERS = [
    # ICT University Teachers
    {
        "name": "Prof. Martin Atangana",
        "phone": "677111222", 
        "email": "martin.atangana@ictuniversity.edu.cm",
        "school_id": "ict-university",
        "subjects": ["Database Systems", "Software Engineering"],
        "office": "Block A, Room 101"
    },
    {
        "name": "Dr. Rose Manga",
        "phone": "659333444",
        "email": "rose.manga@ictuniversity.edu.cm", 
        "school_id": "ict-university",
        "subjects": ["Programming Fundamentals", "Data Structures"],
        "office": "Block A, Room 205"
    },
    {
        "name": "Eng. Pierre Ndongo", 
        "phone": "698555666",
        "email": "pierre.ndongo@ictuniversity.edu.cm",
        "school_id": "ict-university", 
        "subjects": ["Network Security", "System Administration"],
        "office": "Block B, Room 301"
    },

    # Polytech Teachers
    {
        "name": "Prof. Catherine Bello",
        "phone": "677777888",
        "email": "catherine.bello@polytech.edu.cm",
        "school_id": "polytech",
        "subjects": ["Structural Analysis", "Construction Materials"], 
        "office": "Engineering Block, Room 401"
    },
    {
        "name": "Dr. Alain Fouda", 
        "phone": "659999000",
        "email": "alain.fouda@polytech.edu.cm",
        "school_id": "polytech",
        "subjects": ["Thermodynamics", "Fluid Mechanics"],
        "office": "Mechanical Lab, Room 201"
    },
    {
        "name": "Eng. Sylvie Abega",
        "phone": "698111333", 
        "email": "sylvie.abega@polytech.edu.cm",
        "school_id": "polytech",
        "subjects": ["Circuit Analysis", "Power Systems"],
        "office": "Electrical Block, Room 105"
    },

    # University of Yaoundé Teachers  
    {
        "name": "Prof. Henri Owono",
        "phone": "677222555",
        "email": "henri.owono@univ-yaounde1.cm", 
        "school_id": "university-yaounde",
        "subjects": ["Anatomy", "Physiology"],
        "office": "Medical Faculty, Room 501"
    }
]

# Sample Academic Data
SAMPLE_GRADES = {
    "student_ict_001": {
        "Database Systems": 85,
        "Programming Fundamentals": 92, 
        "Mathematics": 78,
        "English": 88
    },
    "student_ict_002": {
        "Programming Fundamentals": 76,
        "Mathematics": 82,
        "Physics": 79,
        "English": 85
    },
    "student_poly_001": {
        "Thermodynamics": 89,
        "Fluid Mechanics": 91,
        "Mathematics": 87, 
        "Technical Drawing": 94
    },
    "student_poly_002": {
        "Structural Analysis": 88,
        "Construction Materials": 85,
        "Mathematics": 90,
        "Project Management": 87
    }
}

# Sample Attendance Records
SAMPLE_ATTENDANCE = {
    "student_ict_001": {
        "2024-11-01": "present",
        "2024-11-02": "absent", 
        "2024-11-03": "present",
        "2024-11-04": "late"
    },
    "student_poly_001": {
        "2024-11-01": "present",
        "2024-11-02": "present",
        "2024-11-03": "absent",
        "2024-11-04": "present" 
    }
}

# Fee Information
SCHOOL_FEES = {
    "ict-university": {
        "tuition_per_semester": 450000,  # 450,000 FCFA
        "registration_fee": 25000,
        "library_fee": 15000
    },
    "polytech": { 
        "tuition_per_semester": 500000,  # 500,000 FCFA
        "registration_fee": 30000,
        "lab_fee": 40000
    },
    "university-yaounde": {
        "tuition_per_semester": 200000,  # 200,000 FCFA (public university)
        "registration_fee": 15000,
        "medical_fee": 10000
    }
}