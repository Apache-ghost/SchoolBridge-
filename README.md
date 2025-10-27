# 🏫 SchoolBridge – A Digital Platform for Parent-Teacher Communication and Student Monitoring

## 📘 Project Overview
**SchoolBridge** is a digital communication platform that connects **schools, teachers, and parents** to promote effective collaboration and real-time student monitoring — even in areas with limited internet access.  

It ensures that no parent misses vital updates about their child’s education by providing **online and offline communication channels** (via web, SMS, and USSD).

---
# ⚠️ Problem Statement
Effective communication between parents and teachers is crucial for student success, yet in many schools—especially in developing regions—communication remains **inefficient and inconsistent**.

### Parents often:
- ❌ Miss important school announcements and parent-teacher meetings  
- 📉 Have no structured way to monitor academic progress beyond report cards  
- 🚫 Lack real-time updates on attendance, assignments, or discipline issues  

### Teachers, on the other hand:
- ⏰ Spend hours on manual communication (calls, letters, or physical meetings)  
- 📚 Struggle to keep parents consistently informed about students’ performance  
- 📵 Face challenges engaging parents who lack smartphones or internet access  

### As a result:
- Parental engagement drops  
- Student performance decreases  
- Collaboration between home and school weakens  

---
## 🎯 Project Justification

### 🔹 Why SchoolBridge is Needed
**SchoolBridge** provides a **unified, reliable, and inclusive communication system** connecting schools, teachers, and parents — accessible even without internet.

It helps:
- Close the communication gap between schools and families  
- Deliver **real-time updates** on attendance, assignments, and discipline  
- Support **data-driven decision-making** for teachers and administrators  
- Enable **offline access via SMS and USSD** for low-income parents  
- Promote **accountability, transparency, and collaboration** in education  

---

## ⚙️ The Problem with Centralized Systems
Most existing school communication systems are **centralized**, meaning they depend on a **single central server** to handle all data and requests.

### Centralized Systems Cause:
| Problem | Description |
|----------|-------------|
| 🧩 **Single Point of Failure** | If the main server crashes, all communication stops |
| 🐢 **Slow Performance** | One server handles all users, causing delays |
| 🚫 **Limited Access** | Schools in remote areas face downtime during network outages |
| 📶 **Dependence on Internet** | Parents without smartphones or internet are excluded |
| 🔒 **Data Risk** | Server corruption or failure can lead to data loss |

---

## 🌐 SchoolBridge’s Shift to a Distributed System

To overcome these challenges, **SchoolBridge transitions from a centralized to a distributed architecture**, ensuring **reliability, scalability, and inclusivity**.

### 🧱 How It Works
Instead of one central server, **multiple interconnected nodes** (mini-servers) are deployed — one for each school or region.

Each node:
- Processes communication **locally**
- Stores data on attendance, assignments, and messages  
- **Synchronizes automatically** with other nodes to maintain consistency  
- Continues operating even if another node or region fails  

---

## 🧩 Distributed Architecture Components

### 1. **Distributed Communication Service (Core Service)**
Handles key functions:
- Attendance alerts  
- Report card delivery  
- Fee notifications  
- Messages and event broadcasts  

Each school runs its **own node**, which syncs automatically with others to ensure uninterrupted service.

---

### 2. **Replication & Distributed Data Storage**
- Student data and communication logs are **replicated across multiple databases**  
- Updates propagate asynchronously to ensure **consistency and speed**  
- If one database fails, others continue providing access  
- Guarantees **fault tolerance and high availability**

---

### 3. **Peer-to-Peer (P2P) Communication Layer**
- Enables **direct, real-time interaction** between teachers and parents  
- Uses **secure WebSocket connections** for chat and alerts  
- Reduces dependence on central servers  
- Ensures parents and teachers stay connected even during regional outages  

---

### 4. **Multi-Region Cloud Deployment**
- Nodes are hosted across **multiple cloud regions**  
- Load balancers route users to the nearest active region  
- If one region fails, others take over instantly  
- All regions stay synchronized for **uniform access and reliability**

---
