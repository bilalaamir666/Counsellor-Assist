# Counsellor Assist

An AI-powered counselling assistant for university counsellors. The system combines a React frontend, FastAPI backend, MongoDB, MongoDB Atlas Vector Search, multilingual embeddings, and an LLM to answer counsellor questions using only approved university reference documents.

The application also provides enquiry management, conversation history, document management, authentication, role-based access, and an administrative dashboard.

---

## 1. Features

### Authentication & Roles

* JWT-based authentication
* Password hashing with bcrypt
* Two roles:

  * `admin`
  * `counsellor`
* Protected API endpoints based on user role

### Document Management

* Admin-only document management
* Upload PDF and Markdown documents
* Background document processing
* Processing states:

  * `pending`
  * `processing`
  * `ready`
  * `failed`
* Failure reason stored when processing fails
* PDF page numbers preserved for source citations
* Documents and their chunks can be deleted

### AI Counselling Chat

* Natural-language questions
* Retrieval-Augmented Generation (RAG)
* Answers are generated only from the uploaded reference documents
* Source citations include:

  * document name
  * page number
  * supporting snippet
* Follow-up questions supported through conversation history
* Explicit refusal when information cannot be found in the documents

### Conversation History

* Previous conversations stored in MongoDB
* Counsellors can view conversation history
* Individual conversations can be opened to inspect messages

### Enquiry Management

Counsellors can:

* Create student enquiries
* View enquiries
* Update enquiry status
* Assign counsellors
* Add notes
* Track status history

Supported enquiry statuses:

```text
new
contacted
documents pending
applied
visa in process
closed
```

### Dashboard & Statistics

Admin dashboard provides:

* Total enquiries
* Status distribution
* New enquiries per week
* Top courses
* Average days from enquiry creation to application

Statistics are generated using MongoDB aggregation pipelines.

---

## 2. Technology Stack

### Frontend

* React 19
* TypeScript
* Vite
* CSS

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* PyMuPDF

### Database

* MongoDB
* MongoDB Atlas Vector Search

### Authentication

* JWT
* bcrypt password hashing

### Embeddings

* `intfloat/multilingual-e5-small`
* 384-dimensional embeddings
* Normalized embeddings
* `passage:` prefix for document chunks
* `query:` prefix for user queries

### LLM

The LLM provider is configurable through environment variables.

Current configuration uses:

```text
Provider: Groq
Model: openai/gpt-oss-20b
```

The LLM provider/model can be changed through environment configuration without changing the application architecture.

---

## 3. Project Structure

```text
counsellor-assist/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── database.py
│   │   ├── database_indexes.py
│   │   └── main.py
│   │
│   ├── uploads/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── sample_data/
│   ├── CBIU Student Visa Handbook 2027.pdf
│   ├── CBIU_Fees_2027.pdf
│   ├── Crescent Bay International University - Admissions Guide 2027.pdf
│   └── Crescent Bay International University Student Accommodation FAQ 2027.pdf
│
├── eval/
│   └── questions.json
│
├── scripts/
│   ├── evaluate_rag.py
│   ├── evaluate_refusal.py
│   └── seed_data.py
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Architecture

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         │   React + TypeScript │
                         └──────────┬───────────┘
                                    │ HTTP / JWT
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
       │   MongoDB    │      │ Atlas Vector │      │     Groq     │
       │              │      │    Search    │      │     LLM      │
       │ users        │      │              │      │              │
       │ documents    │      │ embeddings   │      │ answer       │
       │ chunks       │      │ similarity   │      │ generation   │
       │ enquiries    │      └──────────────┘      └──────────────┘
       │ conversations│
       └──────────────┘
```

---

## 5. RAG Architecture

The application uses Retrieval-Augmented Generation instead of fine-tuning the language model.

### Document ingestion

When an admin uploads a document:

```text
Upload
   ↓
Document saved
   ↓
Status = pending
   ↓
Background processing
   ↓
PDF/Markdown extraction
   ↓
Text chunking
   ↓
Embedding generation
   ↓
Chunks stored in MongoDB
   ↓
Status = ready
```

### PDF processing

PDF files are processed using PyMuPDF.

Each extracted chunk stores its original page number so that the final answer can cite the correct page.

### Chunking

Current chunking strategy:

```text
Chunk size: approximately 500 characters
Overlap: approximately 100 characters
```

The overlap helps preserve context between adjacent chunks.

### Embeddings

The system uses:

```text
intfloat/multilingual-e5-small
```

Embedding dimension:

```text
384
```

Documents use:

```text
passage: <chunk text>
```

Queries use:

```text
query: <user question>
```

Embeddings are normalized before storage/retrieval.

### Retrieval

MongoDB Atlas Vector Search retrieves the most relevant chunks using cosine similarity.

The current chat retrieval uses the top 5 chunks.

### Answer generation

Retrieved chunks are provided to the LLM together with strict instructions:

* Use only supplied reference chunks
* Do not use outside knowledge
* Do not invent information
* Refuse when the information is not supported
* Return supporting chunk indexes

The backend then converts the selected chunks into actual document/page/snippet citations.

### Unanswerable questions

If the documents do not contain enough information, the assistant returns:

```text
I could not find this information in the provided documents.
```

No supporting sources are returned for a refused answer.

---

## 6. Why RAG Instead of Fine-Tuning?

RAG was selected because the counselling information is document-based and may change frequently.

Advantages:

* New documents can be uploaded without retraining a model
* Sources can be shown to counsellors
* Page-level citations are possible
* Outdated documents can be removed
* Lower maintenance cost
* Better control over factual grounding

Fine-tuning could be useful for teaching a model a particular response style or workflow, but it is not the preferred solution for frequently changing factual university information.

---

## 7. Database Model

### Users

```text
users
├── _id
├── name
├── email
├── password_hash
├── role
└── created_at
```

### Documents

```text
documents
├── _id
├── filename
├── original_filename
├── file_type
├── status
├── failure_reason
├── uploaded_by
├── created_at
└── updated_at
```

### Chunks

```text
chunks
├── _id
├── document_id
├── content
├── page_number
├── chunk_index
├── embedding
└── created_at
```

### Conversations

```text
conversations
├── _id
├── user_id
├── messages[]
├── created_at
└── updated_at
```

Each message contains:

```text
role
content
sources[]
created_at
```

### Enquiries

```text
enquiries
├── _id
├── student_name
├── student_email
├── student_phone
├── nationality
├── course
├── intake
├── status
├── assigned_counsellor
├── notes[]
├── status_history[]
├── created_at
└── updated_at
```

---

## 8. MongoDB Indexes

The application creates indexes for commonly queried fields.

Current indexes include:

```text
users.email
documents.status
documents.uploaded_by
conversations.user_id + updated_at
enquiries.status
enquiries.assigned_counsellor
enquiries.created_at
```

The users email index is unique.

MongoDB Atlas Vector Search uses:

```text
Index: vector_index
Path: embedding
Dimensions: 384
Similarity: cosine
```

---

## 9. Pagination

List endpoints support pagination using:

```text
?page=1&limit=10
```

Pagination response format:

```json
{
  "page": 1,
  "limit": 10,
  "total": 30,
  "pages": 3,
  "items": []
}
```

Pagination is available for:

* Documents
* Conversations
* Enquiries

The API validates:

```text
page >= 1
1 <= limit <= 100
```

---

## 10. API Endpoints

### Authentication

```text
POST /auth/login
```

### Documents

```text
POST   /documents
GET    /documents
GET    /documents/{document_id}
DELETE /documents/{document_id}
```

Document management requires admin access.

### Chat

```text
POST /chat/ask
```

### Conversations

```text
GET /conversations
GET /conversations/{conversation_id}
```

### Enquiries

```text
POST  /enquiries
GET   /enquiries
GET   /enquiries/{enquiry_id}
PATCH /enquiries/{enquiry_id}
POST  /enquiries/{enquiry_id}/notes
```

### Statistics

```text
GET /stats/enquiries
```

Statistics require admin access.

---

## 11. Setup

### Requirements

Install:

* Python 3.10+
* Node.js
* npm
* MongoDB or MongoDB Atlas account

### Backend

Open a terminal:

```powershell
cd backend
```

Create/activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### Environment variables

Create:

```text
.env
```

using `.env.example` as the template.

Example:

```env
MONGO_URI=your_mongodb_connection_string
DATABASE_NAME=counsellor_assist

JWT_SECRET=your_secure_jwt_secret

LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_groq_api_key
```

Never commit `.env` or real API keys.

### Start backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 12. Seed Data

The project includes a seed script for fictional users and enquiries.

Run:

```powershell
cd scripts
python seed_data.py
```

The seed data contains:

* 1 admin
* 1 counsellor
* 30 fictional enquiries
* Data distributed across the previous two months
* Multiple enquiry statuses
* Multiple courses
* Notes and status histories

---

## 13. Reference Documents

The project includes four fictional university reference documents for:

1. Admissions
2. Tuition, fees and refunds
3. Student accommodation
4. Student visa requirements

The fictional institution is:

```text
Crescent Bay International University (CBIU)
```

These documents are intentionally fictional and are included only for demonstrating the RAG system.

---

## 14. Evaluation

The evaluation dataset is located at:

```text
eval/questions.json
```

It contains:

* 12 answerable questions
* 3 unanswerable questions

The evaluation checks whether the expected document/page appears within the retrieved results.

Run:

```powershell
python scripts/evaluate_rag.py
```

### Current evaluation result

```text
Answerable questions: 12

Top-1 accuracy: 9/12 (75.00%)
Top-3 accuracy: 11/12 (91.67%)
Top-5 accuracy: 11/12 (91.67%)

Unanswerable questions: 3
```

Unanswerable questions are separately evaluated using:

```powershell
python scripts/evaluate_refusal.py
```

Current refusal evaluation:

```text
Passed: 3/3
Failed: 0/3
Refusal accuracy: 100.00%
```

The main retrieval miss is one answerable question where the expected page was not included in the top five retrieved chunks.

---

## 15. Security

The application uses:

* JWT authentication
* bcrypt password hashing
* Role-based authorization
* Environment variables for secrets
* `.gitignore` protection for `.env`
* Protected admin document endpoints
* Protected conversation access
* Protected user-specific conversation history

No API keys or passwords should be committed to the repository.

---

## 16. Error Handling & Validation

The API uses Pydantic validation for request data.

Examples include:

* Valid email validation
* Minimum/maximum string lengths
* Valid enquiry statuses
* Required fields
* Pagination limits
* Invalid document IDs
* Invalid conversation IDs
* Unauthorized requests
* Forbidden role-based requests
* Missing documents/enquiries/conversations

The API uses appropriate HTTP status codes including:

```text
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
```

---

## 17. Known Limitations

### Retrieval similarity

Some unrelated chunks can receive relatively close vector similarity scores because semantic embeddings may consider different university-related topics similar.

The current evaluation still achieves:

```text
91.67% Top-5 retrieval accuracy
100% refusal accuracy
```

Further retrieval improvements could include:

* similarity score thresholds
* metadata filtering
* hybrid keyword + vector search
* reranking
* improved chunking

### Pagination implementation

The current API supports pagination, but some list services retrieve the collection and then slice the results in Python.

For a larger production dataset, pagination should be moved directly into MongoDB using:

```text
skip()
limit()
```

or cursor-based pagination.

### Counsellor assignment

The current interface supports assigning a counsellor ID. A future improvement would be a dedicated counsellor endpoint and dropdown populated from available counsellors.

---

## 18. Future Improvements

Potential next steps:

1. Improve retrieval with hybrid search/reranking
2. Add document re-processing controls
3. Add a proper counsellor selection dropdown
4. Add MongoDB-level pagination
5. Add richer source display in conversation history
6. Add automated backend tests
7. Add more evaluation questions
8. Add document versioning
9. Add audit logging
10. Add production deployment configuration
11. Add more detailed analytics
12. Add streaming LLM responses for faster perceived response time

---

## 19. Demo Flow

Recommended demo sequence:

```text
1. Login as admin
2. Show dashboard statistics
3. Show uploaded reference documents
4. Ask an answerable RAG question
5. Show source document + page citation
6. Ask an unanswerable question
7. Show explicit refusal
8. Open conversation history
9. Create/update a student enquiry
10. Add an enquiry note
11. Change enquiry status
12. Show status history
13. Login as counsellor
14. Demonstrate role restrictions
```

---

## 20. Git History

Development was completed using incremental Git commits rather than one squashed commit.

Major milestones include:

```text
Initialize Git repository
Set up project structure
Set up Python backend environment
Connect FastAPI to MongoDB
Add JWT authentication and role-based access
Add Phase 3 data models and database services
Add vector retrieval with MongoDB Atlas
Complete RAG chat and source citations
Add enquiries and dashboard statistics
Add frontend chat and enquiry management
Complete counsellor assist application
```

---

## 21. Status

The application currently includes:

* [x] React frontend
* [x] FastAPI backend
* [x] MongoDB
* [x] JWT authentication
* [x] Role-based access
* [x] Document upload
* [x] Background document processing
* [x] PDF page extraction
* [x] Embeddings
* [x] MongoDB Atlas Vector Search
* [x] RAG chat
* [x] Source citations
* [x] Conversation history
* [x] Enquiry management
* [x] Notes and status history
* [x] Dashboard statistics
* [x] Seed data
* [x] Evaluation dataset
* [x] Retrieval evaluation
* [x] Refusal evaluation
* [x] Frontend production build
* [x] Git version history

---

## License

This project was developed as a technical assignment/demo application.
