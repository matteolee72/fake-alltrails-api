import requests

BASE_URL = "http://localhost:8000"

def test_get_trails():
    response = requests.get(f"{BASE_URL}/trails")
    print("length of trails: " + str(len(response.json())))
    print("GET /trails:", response.json())

def test_create_trail():
    data = {
        "name": "Test Trail",
        "location": "Test Location",
        "difficulty": "Moderate",
        "length": 2.5,
        "duration": 45,
        "elevation_gain": 150,
        "type": "Circular"
    }
    response = requests.post(f"{BASE_URL}/trails", json=data)
    print("POST /trails:", response.json())
    return response.json()["id"]

def test_update_trail(trail_id):
    data = {"duration": 50}
    print("Before 1st PUT, duration: " + str(requests.get(f"{BASE_URL}/trails/{trail_id}").json()["duration"]))
    response = requests.put(f"{BASE_URL}/trails/{trail_id}", json=data)
    print("after 1st PUT, duration: " + str(requests.get(f"{BASE_URL}/trails/{trail_id}").json()["duration"]))
    response = requests.put(f"{BASE_URL}/trails/{trail_id}", json=data)
    response = requests.put(f"{BASE_URL}/trails/{trail_id}", json=data)
    response = requests.put(f"{BASE_URL}/trails/{trail_id}", json=data)
    print("PUT 3 more times, duration is:" + str(requests.get(f"{BASE_URL}/trails/{trail_id}").json()["duration"]))
    print(f"PUT /trails/{trail_id}:", response.json())

def test_delete_trail(trail_id):
    response = requests.delete(f"{BASE_URL}/trails/{trail_id}")
    if response.status_code == 404:
        print("Idempotent, I send the same DELETE request, unable to delete non-existent resource :)")
    print(f"DELETE /trails/{trail_id} status code:", response.status_code)

def create_test_trail(difficulty="Moderate"):
    data = {
        "name": "Batch Test Trail",
        "location": "Test Location",
        "difficulty": difficulty,
        "length": 3.0,
        "duration": 30,
        "elevation_gain": 100,
        "type": "Circular"
    }
    response = requests.post(f"{BASE_URL}/trails", json=data)
    response.raise_for_status()
    return response.json()

def test_batch_delete_valid():
    """Test batch deletion with the correct admin token."""
    # Create two test trails with a moderate difficulty.
    trail1 = create_test_trail("Moderate")
    trail2 = create_test_trail("Moderate")
    print("Num Trails with moderate difficulty: " + str(len(requests.get(f"{BASE_URL}/trails?difficulty=Moderate").json())))
    print(requests.get(f"{BASE_URL}/trails?difficulty=Moderate").json())

    
    headers = {"X-Admin-Token": "secret-admin-token"}
    # Issue the batch delete for trails with difficulty "BatchTest"
    delete_response = requests.delete(f"{BASE_URL}/trails?difficulty=Moderate", headers=headers)
    assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}"
    
    # Verify that no trails with difficulty "Moderate" remain.
    trails_after = requests.get(f"{BASE_URL}/trails").json()
    for trail in trails_after:
        assert trail["difficulty"] != "Moderate", "Test trail still exists after deletion!"
    print("Num Trails with moderate difficulty (After Batch Delete): " + str(len(requests.get(f"{BASE_URL}/trails?difficulty=Moderate").json())))        
    print(requests.get(f"{BASE_URL}/trails?difficulty=Moderate").json())



def test_batch_delete_invalid_token():
    """Test batch deletion with an invalid admin token."""
    # Create a test trail with a different unique difficulty.
    headers = {"X-Admin-Token": "wrong-token"}
    print("Num Trails with moderate difficulty: " + str(len(requests.get(f"{BASE_URL}/trails?difficulty=Easy").json())))
    print(requests.get(f"{BASE_URL}/trails?difficulty=Easy").json())
    response = requests.delete(f"{BASE_URL}/trails?difficulty=Easy", headers=headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    json_response = response.json()
    assert "Not authorized" in json_response["detail"]
    print("Num Trails with moderate difficulty (After Batch Delete Attempt with invalid token/no authorization): " + str(len(requests.get(f"{BASE_URL}/trails?difficulty=Easy").json())))
    print(requests.get(f"{BASE_URL}/trails?difficulty=Easy").json())

def test_batch_delete_no_matching_trails():
    """Test batch deletion when no trails match the given condition."""
    headers = {"X-Admin-Token": "secret-admin-token"}
    # Use a difficulty value that doesn't exist.
    response = requests.delete(f"{BASE_URL}/trails?difficulty=Moderate", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    json_response = response.json()
    assert "No trails match" in json_response["detail"]

if __name__ == "__main__":
    test_get_trails()
    new_trail_id = test_create_trail()
    test_get_trails()
    test_update_trail(new_trail_id)
    test_delete_trail(new_trail_id)
    test_delete_trail(new_trail_id)
    test_delete_trail(new_trail_id)
    test_get_trails()

    test_batch_delete_valid()
    test_batch_delete_invalid_token()
    test_batch_delete_no_matching_trails()