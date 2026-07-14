import os
import time
import requests

api_key = os.environ["MINIMAX_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}


# --- Step 1: Create a video generation task ---
# The API supports four modes: text-to-video, image-to-video, first-and-last-frame-video, and subject-reference-video.
# Each function below starts an asynchronous task and returns a unique task_id.

def invoke_text_to_video() -> str:
    """(Mode 1) Create a video generation task from a text description."""
    url = "https://api.minimax.io/v1/video_generation"
    payload = {
        # 'prompt' is the key parameter that defines the video’s content and motion.
        "prompt": "A tiktok dancer is dancing on a drone, doing flips and tricks.",
        "model": "MiniMax-Hailuo-2.3",
        "duration": 6,
        "resolution": "1080P",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    task_id = response.json()["task_id"]
    return task_id

def invoke_image_to_video() -> str:
    """(Mode 2) Create a video generation task using a first-frame image and text description."""
    url = "https://api.minimax.io/v1/video_generation"
    payload = {
        # In image-to-video mode, 'prompt' describes the dynamic scene evolution from the first image.
        "prompt": "Vertical 9:16 video. A tired-looking woman sits at the edge of her bed as soft morning light enters the room.",
        # 'first_frame_image' specifies the starting frame of the video.
        "first_frame_image": "https://raw.githubusercontent.com/shirley-goose/pics/main/071301.png",
        "model": "MiniMax-Hailuo-2.3",
        "duration": 6,
        "resolution": "768P",
        # "aspect_ratio": "9:16",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()
    print(response_json)
    task_id = response.json()["task_id"]
    return task_id

# def invoke_start_end_to_video() -> str:
#     """(Mode 3) Create a video generation task using a first-frame image, last-frame image and text description."""
#     url = "https://api.minimax.io/v1/video_generation"
#     payload = {
#     "prompt": "A little girl grow up.",
#     # 'first_frame_image' specifies the starting frame of the video.
#     "first_frame_image": "https://filecdn.minimax.chat/public/fe9d04da-f60e-444d-a2e0-18ae743add33.jpeg",
#     # 'last_frame_image' specifies the last frame of the video.
#     "last_frame_image": "https://filecdn.minimax.chat/public/97b7cd08-764e-4b8b-a7bf-87a0bd898575.jpeg",
#     "model": "MiniMax-Hailuo-02",
#     "duration": 6,
#     "resolution": "1080P"
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     response.raise_for_status()
#     task_id = response.json()["task_id"]
#     return task_id

# def invoke_subject_reference() -> str:
#     """(Mode 4) Create a video generation task using a subject's face photo and a text description."""
#     url = "https://api.minimax.io/v1/video_generation"
#     payload = {
#     "prompt": "On an overcast day, in an ancient cobbled alleyway, the model is dressed in a brown corduroy jacket paired with beige trousers and ankle boots, topped with a vintage beret. The shot starts from over the model's shoulder, following his steps as it captures his swaying figure. Then, the camera moves slightly sideways to the front, showcasing his natural gesture of adjusting the beret with a smile. Next, the shot slightly tilts down, capturing the model's graceful stance as he leans against the wall at a corner. The video concludes with an upward shot, showing the model smiling at the camera. The lighting and colors are natural, giving the footage a cinematic quality.",
#     "subject_reference": [
#         {
#             "type": "character",
#             "image": [
#                 "https://filecdn.minimax.chat/public/54be8fbe-5694-4422-9c95-99cf785eb90e.PNG"
#             ],
#         }
#     ],
#     "model": "S2V-01",
#     "duration": 6,
#     "resolution": "1080P",
# }
#     response = requests.post(url, headers=headers, json=payload)
#     response.raise_for_status()
#     task_id = response.json()["task_id"]
#     return task_id


# --- Step 2: Poll task status ---
# Since video generation is time-consuming, the API works asynchronously.
# After submitting a task, poll its status using the task_id until it succeeds or fails.
def query_task_status(task_id: str):
    """Poll task status by task_id until it succeeds or fails."""
    url = "https://api.minimax.io/v1/query/video_generation"
    params = {"task_id": task_id}
    while True:
        # A recommended polling interval is 10 seconds to avoid unnecessary server load.
        time.sleep(10)
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        status = response_json["status"]
        print(f"Current task status: {status}")
        # On success, the API returns a 'file_id' to fetch the video file.
        if status == "Success":
            return response_json["file_id"]
        elif status == "Fail":
            raise Exception(f"Video generation failed: {response_json.get('error_message', 'Unknown error')}")


# --- Step 3: Retrieve and save the video file ---
# When the task succeeds, the response includes a file_id instead of a direct download link.
# This function fetches the download URL and saves the video locally.
def fetch_video(file_id: str):
    """Retrieve the download URL from file_id and save the video locally."""
    url = "https://api.minimax.io/v1/files/retrieve"
    params = {"file_id": file_id}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    download_url = response.json()["file"]["download_url"]

    with open("output.mp4", "wb") as f:
        video_response = requests.get(download_url)
        video_response.raise_for_status()
        f.write(video_response.content)
    print("Video successfully saved as output.mp4")


# --- Main process: end-to-end example ---
# Demonstrates the full workflow from task creation to video retrieval.
if __name__ == "__main__":
    # Choose a task creation mode
    # task_id = invoke_text_to_video()  # Mode 1: Text-to-Video
    task_id = invoke_image_to_video() # Mode 2: Image-to-Video
    # task_id = invoke_start_end_to_video() # Mode 3: Start-End-to-Video
    # task_id = invoke_subject_reference() # Mode 4: Subject Reference
    print(f"Video generation task submitted, Task ID: {task_id}")
    file_id = query_task_status(task_id)
    print(f"Task succeeded, File ID: {file_id}")
    fetch_video(file_id)