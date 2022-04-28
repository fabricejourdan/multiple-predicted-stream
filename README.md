## Multiple Predcited RTSP Streaming with Flask and Open-CV

```sh
conda create --name multiple-camera-stream python==3.9
pip install -r requirements.txt
```
#### Config.json allows user to define :
#### - RTPS streams : key "streams"
#### - Crowd Counting model as onnx file : key "model_filepath"
#### - Time in seconds between 2 predicted results : key "snapshot_time"
#### - parameters to present image with density map and counter : key "output"
```sh
{
    "streams": ["rtsp://127.0.0.1:8554/stream-1.sdp", "rtsp://127.0.0.1:8554/stream-2.sdp", "rtsp://www.iafoule.fr/test.sdp"],
    "snapshot_time": 2.0,
    "model_filepath": "/workspace/home/jourdanfa/mobilecount_20220422.onnx",
    "output": {
        "mode": "image_with_density_map",
        "alpha_type": "std",
        "alpha_weight": 0.6,
        "factor": 1.0
    }
}
```

### Run Server

```sh
python app.py
```



## Credit

Learn More about Streaming with flask

- https://blog.miguelgrinberg.com/post/video-streaming-with-flask
