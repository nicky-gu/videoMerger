from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, AudioFileClip
import requests
import os
from io import BytesIO
from minio import Minio
from config import ACCESS_TOKEN, MINIO_CONFIG, BUCKET_NAME

app = Flask(__name__)

# 初始化 MinIO 客户端
minio_client = Minio(
    MINIO_CONFIG["endpoint"],
    access_key=MINIO_CONFIG["access_key"],
    secret_key=MINIO_CONFIG["secret_key"],
    secure=False
)

@app.route('/create_video', methods=['POST'])
def create_video():
    # 验证访问令牌
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer ') or auth_header.split()[1] != ACCESS_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.json
        image_url = data['image_url']
        audio_url = data['audio_url']

        # 下载图像
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image = BytesIO(image_response.content)

        # 下载音频
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        audio = BytesIO(audio_response.content)

        # 创建视频
        image_clip = ImageClip(image).set_duration(5)  # 假设视频时长为5秒
        audio_clip = AudioFileClip(audio)
        video = image_clip.set_audio(audio_clip)

        video_path = '/tmp/output_video.mp4'  # 使用临时目录来生成文件
        video.write_videofile(video_path, codec='libx264')

        # 上传视频到 MinIO
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
        minio_client.fput_object(BUCKET_NAME, "output_video.mp4", video_path)

        # 删除本地生成的视频
        if os.path.exists(video_path):
            os.remove(video_path)

        # 构建视频 URL
        video_url = f"http://{MINIO_CONFIG['endpoint']}/{BUCKET_NAME}/output_video.mp4"
        return jsonify({'message': 'Video created successfully', 'video_url': video_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))