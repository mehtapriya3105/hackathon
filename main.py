from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import List
from pydantic import BaseModel
from typing import List
import uvicorn

# Pydantic model for item
# Define Address model
class Address(BaseModel):
    city: str
    state: str
    country: str

# Define the main Patient model
class Patient(BaseModel):
    medical_history: List[str]
    symptoms: List[str]
    address: Address
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

# Pydantic models for request validation
class Disease(BaseModel):
    Disease: str
    Symptoms: List[str]
    PatientIds: List[int]


# Model for response to return _id with object data
class PatientResponse(Patient):
    id: str

class DiseaseResponse(Disease):
    id: str  # Adding the ID to the response

class UserResponse(User):
    id: str  # Adding the ID to the response

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")  # Update with your MongoDB connection string
db = client["admin"]
collection = db["Patient"]
db_disease = db["Disease"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users", response_model=UserResponse)
async def create_user(user: User):
    # Insert the user into the MongoDB collection
    result = collection.insert_one(user.dict())
    
    # Return the inserted user's ID
    return {"id": str(result.inserted_id), **user.dict()}

@app.get("/users", response_model=List[dict])
async def get_items():
    # Fetch all documents from the collection
    items = list(collection.find())
    print(items)
    # Optionally, remove the MongoDB-specific "_id" field
    for item in items:
        item["_id"] = str(item["_id"])

    return items

@app.put("/users/{id}", response_model=UserResponse)
async def update_user(id: str, user: User):
    # Convert the string id to ObjectId for MongoDB
    user_id = ObjectId(id)

    # Find the existing user by id
    existing_user = collection.find_one({"_id": user_id})

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user details
    update_result = collection.update_one(
        {"_id": user_id},
        {"$set": user.dict()}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update user")

    # Return the updated user details along with the ID
    updated_user = collection.find_one({"_id": user_id})
    updated_user["id"] = str(updated_user["_id"])
   

    return updated_user


@app.get("/patients", response_model=List[dict])
async def get_items():
    # Fetch all documents from the collection
    items = list(collection.find())
    print(items)
    # Optionally, remove the MongoDB-specific "_id" field
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
    
    return items

@app.get("/disease", response_model=List[dict])
async def get_items():
    # Fetch all documents from the collection
    items = list(db_disease.find())
    print(items)
    # Optionally, remove the MongoDB-specific "_id" field
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
    
    return items

@app.post("/patients", response_model=PatientResponse)
async def create_patient(patient: Patient):
    # Insert the patient into the MongoDB collection
    result = collection.insert_one(patient.dict())
    
    # Return the inserted patient's ID
    return {"id": str(result.inserted_id), **patient.dict()}

@app.post("/disease", response_model=DiseaseResponse)
async def create_disease(disease: Disease):
    # Insert the disease into the MongoDB collection
    result = db_disease.insert_one(disease.dict())
    
    # Return the inserted disease's ID along with the data
    return {"id": str(result.inserted_id), **disease.dict()}

# PUT request to update a patient
@app.put("/patients/{id}", response_model=PatientResponse)
async def update_patient(id: str, patient: Patient):
    # Convert the string id to ObjectId for MongoDB
    patient_id = ObjectId(id)

    # Find the existing patient by id
    existing_patient = collection.find_one({"_id": patient_id})

    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update the patient details
    update_result = collection.update_one(
        {"_id": patient_id},
        {"$set": patient.dict()}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update patient")

    # Return the updated patient details along with the ID
    updated_patient = collection.find_one({"_id": patient_id})
    updated_patient["id"] = str(updated_patient["_id"])
   

    return updated_patient

# PUT request to update a patient
@app.put("/disease/{id}", response_model=DiseaseResponse)
async def update_disease(id: int, disease: Disease):
    # Convert the string id to ObjectId for MongoDB
    disease_id = id

    # Find the existing patient by id
    existing_patient = db_disease.find_one({"_id": disease_id})

    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update the patient details
    update_result = db_disease.update_one(
        {"_id": disease_id},
        {"$set": disease.dict()}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update patient")

    # Return the updated patient details along with the ID
    updated_patient = db_disease.find_one({"_id": disease_id})
    updated_patient["id"] = str(updated_patient["_id"])
    

    return updated_patient


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)