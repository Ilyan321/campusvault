import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_workflow_ingest_and_query():
    # 1. Simulate Senior Note (C++ Code + Comments on Circular Queue)
    note_code = """
    // Circular Queue Implementation in C++ for Lab Exam
    #include <iostream>
    using namespace std;

    #define SIZE 5
    int queue[SIZE];
    int front = -1, rear = -1;

    // Enqueue operation
    void enqueue(int value) {
        if ((front == 0 && rear == SIZE - 1) || (rear == (front - 1) % (SIZE - 1))) {
            cout << "Queue is Full (Buffer Overflow)!" << endl;
            return;
        } else if (front == -1) { // First element insertion
            front = rear = 0;
            queue[rear] = value;
        } else if (rear == SIZE - 1 && front != 0) {
            rear = 0; // Wrap around to index 0
            queue[rear] = value;
        } else {
            rear++;
            queue[rear] = value;
        }
    }
    """
    
    # Ingest confirmation
    confirm_res = client.post("/api/ingest/confirm", json={
        "file_name": "circular_queue_lab.cpp",
        "file_url": "https://storage.campusvault.internal/uploads/circular_queue_lab.cpp",
        "course_id": "CSE-212",
        "week_number": 5,
        "topic": "Queue Data Structure & Circular Implementations",
        "content": note_code
    })
    
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["success"] is True
    assert "Successfully indexed" in confirm_data["message"]

    # 2. Simulate Junior Query in Week 5 Context
    query_res = client.post("/api/query", json={
        "query": "Yaar circular queue mein rear pointer wrap around kab hota hai?",
        "week_number": 5,
        "course_id": "CSE-212"
    })
    
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert "answer" in query_data
    assert query_data["week_number"] == 5
    assert query_data["course_id"] == "CSE-212"
    print("\n[RAG Generated Answer]:\n", query_data["answer"])

if __name__ == "__main__":
    test_full_workflow_ingest_and_query()
    print("\n✅ End-to-End Ingestion & RAG Pipeline PASSED!")
