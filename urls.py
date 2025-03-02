import datetime
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List,Optional
from pymongo import MongoClient
from bson import ObjectId
import uvicorn

app = FastAPI()
mainUserId = ""
client = MongoClient("mongodb://localhost:27017")
db = client["RareDisease"]
users_collection = db["User"]
patients_collection = db["Patient"]
doctors_collection = db["Doctor"]
diseases_collection = db["Disease"]
chats_collection = db["Chat"]

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str

class Address1(BaseModel):
    street: str
    city: str
    state: str
    country: str
    postal_code: str

class ChatMessage(BaseModel):
    message: str
    sender: str
    time: str

class Patient(BaseModel):
    user_id: str  # Foreign key to User
    medical_history: List[str]
    symptoms: List[str]
    address: Address1
    status: str
    drug_history: List[str]

class User(BaseModel):
    username: str
    password: str
    firstName: str
    lastName: str
    gender: str
    dateOfBirth: str
    email: str
    contact: str
    user_id : str

class Disease(BaseModel):
    Name: str
    Symptoms: List[str]
    PatientIds: List[str]  # Foreign key references to Patient
    DoctorIds: List[str]  # Foreign key references to Doctor

class Doctor(BaseModel):
    user_id: str  # Foreign key to User
    Specialization: str
    ResearchArea: List[str]
    Address: Address1

class Chat(BaseModel):
    PatientId: str  # Foreign key to Patient
    DoctorId: str  # Foreign key to Doctor
    Messages: List[str]
    Time: str

class DoctorUpdate(BaseModel):
    user_id: str
    specialization: Optional[str] = None
    research_area: Optional[List[str]] = None


class newUser(BaseModel):
    email: str
    password: str

@app.post("/user/signup")
def signup(user: User):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_dict = user.dict()
    user_id = users_collection.insert_one(user_dict).inserted_id
    return {"message": "User registered successfully", "user_id": str(user_id)}

@app.post("/user/login")
def login(newUser:newUser):
    user = users_collection.find_one({"email": newUser.email, "password": newUser.password})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": str(user["_id"])}

def is_valid_objectid(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False

# Helper function to serialize MongoDB objects (e.g., ObjectId)
def serialize_mongo_object(obj):
    # If the object is a MongoDB ObjectId, convert it to a string
    if isinstance(obj, ObjectId):
        return str(obj)
    # If the object is a dictionary, recursively convert its values
    elif isinstance(obj, dict):
        return {k: serialize_mongo_object(v) for k, v in obj.items()}
    # If the object is a list, recursively convert its items
    elif isinstance(obj, list):
        return [serialize_mongo_object(item) for item in obj]
    # Return other types unchanged
    return obj

@app.get("/user/data")
def get_user_data(user_id: str):
    # Check if the user_id is a valid ObjectId format
    if not is_valid_objectid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    # Try to fetch the user data from the database
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert the MongoDB response (including ObjectId) into a serializable format
    user = serialize_mongo_object(user)

    return user

@app.put("/user/update")
def update_user(user_id: str, email: str = None, password: str = None):
    update_fields = {}
    if email:
        update_fields["email"] = email
    if password:
        update_fields["password"] = password
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
    return {"message": "User updated successfully"}

@app.get("/patient/details/{user_id}")
def get_patient_details(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    patient = patients_collection.find_one({"user_id": user.get("user_id")})
    response = {
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "gender": user["gender"],
            "dateOfBirth": user["dateOfBirth"],
            "email": user["email"],
            "contact": user["contact"]
        }
    }
    if patient:
        response["patient"] = {
            "id": str(patient["_id"]),
            "user_id": patient["user_id"], 
            "medical_history": patient["medical_history"],
            "symptoms": patient["symptoms"],
            "address": patient["address"],
            "status": patient["status"],
            "drug_history": patient["drug_history"]
        }

    return response

# @app.get("/doctors/details/{user_id}")
# def get_patient_details(user_id: str):
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     patient = patients_collection.find_one({"user_id": user.get("user_id")})
#     response = {
#         "user": {
#             "id": str(user["_id"]),
#             "username": user["username"],
#             "firstName": user["firstName"],
#             "lastName": user["lastName"],
#             "gender": user["gender"],
#             "dateOfBirth": user["dateOfBirth"],
#             "email": user["email"],
#             "contact": user["contact"]
#         }
#     }
#     if patient:
#         response["patient"] = {
#             "id": str(patient["_id"]),
#             "user_id": patient["user_id"], 
#             "medical_history": patient["medical_history"],
#             "symptoms": patient["symptoms"],
#             "address": patient["address"],
#             "status": patient["status"],
#             "drug_history": patient["drug_history"]
#         }

#     return response
@app.get("/doctor/details/{user_id}")
def get_doctor_details(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    doctor = doctors_collection.find_one({"user_id": user.get("user_id")})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor details not found")

    response = {
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "gender": user["gender"],
            "dateOfBirth": user["dateOfBirth"],
            "email": user["email"],
            "contact": user["contact"]
        },
        "doctor": {
            "id": str(doctor["_id"]),
            "user_id": doctor["user_id"],
            "specialization": doctor["Specialization"],
            "research_area": doctor["ResearchArea"],
            "address": doctor["Address"]
        }
    }
    
    return response

@app.post("/patient/add/{user_id}")
def create_patient(user_id: str, patient: Patient):
    try:
        
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        patient_dict = patient.dict()
        patient_dict["user_id"] = user.get("user_id") 

        
        result = patients_collection.insert_one(patient_dict)
        
        return {"message": "Patient record created", "patient_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


   

# Update Patient function
@app.put("/patient/update")
def update_patient(user_id: str, symptoms: List[str] = None, drug_history: List[str] = None):
    # Step 1: Find the user in the user collection by user_id
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 2: Find the associated patient by user_id
    patient = patients_collection.find_one({"user_id": user_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Step 3: Prepare the fields to update
    update_fields = {}
    if symptoms:
        update_fields["symptoms"] = symptoms
    if drug_history:
        update_fields["drug_history"] = drug_history
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Step 4: Update the patient details
    patients_collection.update_one({"user_id": user_id}, {"$set": update_fields})

    # Step 5: Return success message
    return {"message": "Patient updated successfully"}

@app.put("/doctor/update")
def update_doctor(doctor_update: DoctorUpdate):
    # Step 1: Find the user in the user collection by user_id
    user = users_collection.find_one({"_id": ObjectId(doctor_update.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 2: Find the associated doctor by user_id
    doctor = doctors_collection.find_one({"user_id": user.get("user_id")})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Step 3: Prepare the fields to update
    update_fields = {}
    if doctor_update.specialization:
        update_fields["Specialization"] = doctor_update.specialization
    if doctor_update.research_area:
        update_fields["ResearchArea"] = doctor_update.research_area
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Step 4: Update the doctor details
    doctors_collection.update_one({"user_id": doctor_update.user_id}, {"$set": update_fields})

    # Step 5: Return success message
    return {"message": "Doctor updated successfully"}

@app.get("/doctor")
def get_doctor(doctor_id: str):
    doctor = doctors_collection.find_one({"_id": ObjectId(doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.post("/doctor/add")
def create_doctor(id: str, doctor: Doctor):
    try:
        user = users_collection.find_one({"_id": ObjectId(id)})
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        doctor_dict = doctor.dict()
        doctor_dict["user_id"] = user.get("user_id") 
        result =  doctors_collection.insert_one(doctor_dict)
        return {"message": "Doctor record created", "doctor_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")





@app.get("/doctor/details")
def get_doctor_details(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    doctor = doctors_collection.find_one({"user_id": user.get("user_id")})
    response = {
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "gender": user["gender"],
            "dateOfBirth": user["dateOfBirth"],
            "email": user["email"],
            "contact": user["contact"]
        }
    }
    if doctor:
        response["doctor"] = {
            "id": str(doctor["_id"]),
            "user_id": doctor["user_id"],
            "specialization": doctor["Specialization"],
            "research_area": doctor["ResearchArea"],
            "address": doctor["Address"]
        }

    return response

def serialize_mongo_object(mongo_obj):
    """Convert MongoDB object to a serializable format (convert ObjectId)."""
    if mongo_obj:
        mongo_obj["_id"] = str(mongo_obj["_id"])  # Convert ObjectId to string
    return mongo_obj

@app.get("/get_patients_by_disease")
def get_patients_by_disease(disease: str):
    # Find the disease in the diseases collection
    disease_data = diseases_collection.find_one({"Name": disease})
    
    if not disease_data:
        return {"error": "Disease not found"}
    
    # Get patient IDs related to the disease
    patient_ids = disease_data.get("PatientIds", [])

    # Find patients based on the patient IDs
    patients = patients_collection.find({"user_id": {"$in": patient_ids}})
    
    # Fetch users' information
    users_data = []
    for patient in patients:
        user = users_collection.find_one({"user_id": patient["user_id"]})
        if user:
            users_data.append({
                "user_id": user["user_id"],
                "firstName": user.get("firstName", ""),
                "lastName": user.get("lastName", ""),
                "gender": user.get("gender", ""),
                "dateOfBirth": user.get("dateOfBirth", ""),
                "email": user.get("email", ""),
                "contact": user.get("contact", ""),
                "address": patient.get("address"),
                "medical_history": patient.get("medical_history", []),
                "symptoms": patient.get("symptoms", []),
                "status": patient.get("status", ""),
                "drug_history": patient.get("drug_history", [])
            })
    
    return {"patients": users_data}



@app.get("/chat")
def get_chat(patient_id: str, doctor_id: str):
    chat = chats_collection.find_one({"PatientId": patient_id, "DoctorId": doctor_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

# @app.post("/chat")
# def create_chat(chat: Chat):
#     chat_dict = chat.dict()
#     chats_collection.insert_one(chat_dict)
#     return {"message": "Chat created successfully"}



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            data["timestamp"] = datetime.utcnow()
            # Save message to MongoDB
            await chats_collection.insert_one(data)
            # Broadcast message to all connected clients
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)



if __name__ == "_main_":
    uvicorn.run(app, host="0.0.0.0", port=8000)