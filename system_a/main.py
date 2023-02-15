import torch
import os
import cv2
import uuid
import requests
from datetime import datetime

evidences_dir = 'evidences'
model_weights = 'weights.pt'
mac_camera = 'EB:DE:1E:46:A3:79'
api_url = 'http://localhost:8000'
api_user = {'username': 'admin', 'password': 'Senai@2023'}
token_access = ''
token_refresh = ''
datetime_format = f'%Y-%m-%dT%H:%M:%S.%f'

def auth_api(url, user):
    print(f'Doing loggin with user: {user["username"]}')
    response = requests.post(f'{url}/api/auth/', data=user)

    if response.status_code == 200:
        data = response.json()
        return data['access'], data['refresh']
    elif response.status_code == 400:
        print(data['message'])

    print('Error to auth in API!')
    exit(1)

def refresh_token(url, token, refresh, user):
    print(f'Refreshing token, user: {user["username"]}')
    response = requests.post(f'{url}/api/auth/refresh/', headers={'Authorization': f'Bearer {token}'}, data={'refresh': refresh})

    if response.status_code == 401:
        access, refresh = auth_api(url, user)
        return access, refresh
    elif response.status_code == 200:
        data = response.json()
        return data['access'], refresh

    print('Error to refresh token!')
    exit(1)

def post_evidence(url, token, data):
    response = requests.post(f'{url}/api/occurrence', headers={'Authorization': f'Bearer {token}'}, data=data)

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        return False
    elif response.status_code == 400:
        print(data['message'])

    print('Error to post evidence!')
    exit(1)


if not os.path.exists(evidences_dir):
    os.mkdir(evidences_dir)

model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_weights)

token_access, token_refresh = auth_api(api_url, api_user)
print(f'Logged with user: {api_user["username"]}')

capture = cv2.VideoCapture(0)
if not capture.isOpened():
    print("Error to open camera!")

last_frame_detection = 0

while True:
    time_now = datetime.now().strftime(datetime_format)
    ret, frame = capture.read()

    if not ret:
        print("Can't receive frame!")
        break

    results = model(frame).crop(save=False)
    total_detections = len(results)

    if total_detections > last_frame_detection:
        for result in results:
            object_class = result['label'].split()[0]
            evidence_path = f'{evidences_dir}/{uuid.uuid4()}-{object_class}.jpg'

            if not cv2.imwrite(evidence_path, result['im']):
                print('Error to save evidece image!')
                exit(1)

            full_path = os.path.abspath(evidence_path).replace('\\', '/')

            data = {
                'mac_address': mac_camera,
                'object_class': object_class,
                'evidence_url': f'file://{full_path}',
                'occurrence_time': time_now
            }

            if not post_evidence(api_url, token_access, data):
                token_access, token_refresh = refresh_token(api_url, token_access, token_refresh, api_user)
                post_evidence(api_url, token_access, data)
            
            print(f'Evidence class "{object_class}" saved: {evidence_path}.')

    last_frame_detection = total_detections
