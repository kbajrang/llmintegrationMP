from pymongo import MongoClient
import os

# ======= USER INPUT ========
EMAIL = "bajrangkailasa6@gmail.com"
ROOM_ID = "123456"
FILE_PATH = r"D:/MajorProject/llmintegration/Java_interview.txt"
# ===========================

# ✅ Correct Mongo URI for your cluster
MONGO_URI = "mongodb+srv://KailasaBajrang:Bajjusatya@cluster0.spg3xdo.mongodb.net/?retryWrites=true&w=majority"

# ✅ Connect to SmartInterviewSystem database
client = MongoClient(MONGO_URI)
db = client["SmartInterviewSystem"]
collection = db["Savedtranscripts"]

# ✅ Ensure file exists
if not os.path.exists(FILE_PATH):
    print("❌ File not found:", FILE_PATH)
    exit()

# ✅ Read transcript content
with open(FILE_PATH, "r", encoding="utf-8") as f:
    transcript_text = f.read()

# ✅ Insert into MongoDB
result = collection.insert_one({
    "email": EMAIL,
    "roomId": ROOM_ID,
    "transcript_text": transcript_text
})

print(f"✅ Transcript uploaded for: {EMAIL} | MongoDB _id: {result.inserted_id}")
