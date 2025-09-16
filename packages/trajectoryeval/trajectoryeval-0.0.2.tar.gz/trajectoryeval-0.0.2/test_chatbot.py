import requests
import json
from uuid import uuid4

def test_chatbot():
    """Test the FastAPI chatbot"""
    base_url = "http://localhost:8001"  # Changed port to 8001
    test_user_id = str(uuid4())
    print(" Testing Simple LLM Chatbot...")
    
    # Test 1: New conversation
    print("\n1️⃣ Starting new conversation...")
    response1 = requests.post(f"{base_url}/new-conversation", json={
        "message": "Hello! What's the weather like today?",
        "user_id": test_user_id
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        conversation_id = data1["conversation_id"]
        print(f"✅ New conversation created: {conversation_id}")
        print(f" Response: {data1['response']}")
    else:
        print(f"❌ Error: {response1.text}")
        return
    
    # Test 2: Continue conversation
    print(f"\n2️⃣ Continuing conversation {conversation_id}...")
    response2 = requests.post(f"{base_url}/chat", json={
        "message": "Can you tell me a joke?",
        "conversation_id": conversation_id,
        "user_id": test_user_id
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"✅ Continued conversation")
        print(f" Response: {data2['response']}")
    else:
        print(f"❌ Error: {response2.text}")
    
    # Test 3: Another message in same conversation
    print(f"\n3️⃣ Another message in conversation {conversation_id}...")
    response3 = requests.post(f"{base_url}/chat", json={
        "message": "What's 2 + 2?",
        "conversation_id": conversation_id,
        "user_id": test_user_id
    })
    
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"✅ Message sent")
        print(f" Response: {data3['response']}")
    else:
        print(f"❌ Error: {response3.text}")
    
    # Test 4: Get conversation history
    print(f"\n4️⃣ Getting conversation history for {conversation_id}...")
    response4 = requests.get(f"{base_url}/conversations/{conversation_id}")
    
    if response4.status_code == 200:
        data4 = response4.json()
        print(f"✅ Conversation history:")
        for msg in data4["messages"]:
            print(f"   {msg['role']}: {msg['content']}")
    else:
        print(f"❌ Error: {response4.text}")
    
    # Test 5: List all conversations
    print(f"\n5️⃣ Listing all conversations...")
    response5 = requests.get(f"{base_url}/conversations")
    
    if response5.status_code == 200:
        data5 = response5.json()
        print(f"✅ Conversations:")
        for conv in data5["conversations"]:
            print(f"   {conv['conversation_id']}: {conv['message_count']} messages")
    else:
        print(f"❌ Error: {response5.text}")

def interactive_chat():
    """Interactive chat session"""
    base_url = "http://localhost:8001"  # Changed port to 8001
    
    print("\n💬 Interactive Chat Session")
    print("Type 'quit' to exit, 'new' to start new conversation")
    
    conversation_id = None
    test_user_id = str(uuid4())
    
    while True:
        message = input("\n👤 You: ").strip()
        
        if message.lower() == 'quit':
            break
        elif message.lower() == 'new':
            conversation_id = None
            print("🆕 Starting new conversation...")
            continue
        elif not message:
            continue
        
        try:
            if conversation_id:
                # Continue existing conversation
                response = requests.post(f"{base_url}/chat", json={
                    "message": message,
                    "conversation_id": conversation_id,
                    "user_id": test_user_id
                })
            else:
                # Start new conversation
                response = requests.post(f"{base_url}/new-conversation", json={
                    "message": message,
                    "user_id": test_user_id
                })
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                print(f" Assistant: {data['response']}")
                print(f" Conversation ID: {conversation_id}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run automated tests")
    print("2. Start interactive chat")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_chatbot()
    elif choice == "2":
        interactive_chat()
    else:
        print("Invalid choice. Running tests...")
        test_chatbot()
