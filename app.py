import sys

sys.path.append("../ia-foule-lab/")

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from iafoule.ccmodels.inference import CCModelInference
from iafoule.density import image_with_density_map
from config import Config

from flask import Flask, render_template, Response

app = Flask(__name__)

cfg = Config("config.json").get_config()
print('cfg:', cfg)

snapshot_time = cfg["snapshot_time"]
print('snapshot_time:', snapshot_time)

ccmodel = CCModelInference(cfg["model_filepath"])
print(ccmodel)

streams = cfg["streams"]
print('streams:', streams)

output = cfg["output"]
print('output:', output)
display_mode = output["mode"]
# values : image_with_density_map, raw_image
print('display_mode:', display_mode)


@app.route('/predicted_stream/<string:stream_id>/', methods=["GET"])
def predicted_stream(stream_id):
    """Predicted Streaming route. The steam_id corresponds to the stream number defined in utils.py."""
    return Response(get_frame(stream_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/stream/<string:stream_id>/', methods=["GET"])
# def stream(stream_id):
#     """Predicted Streaming route. The steam_id corresponds to the stream number defined in utils.py."""
#     return Response(get_frame(stream_id, display='stream'))


@app.route('/', methods=["GET"])
def index():
    """Predicted Streaming Console route."""
    stream_ids = get_stream_ids()
    print("stream_ids:", stream_ids)
    return render_template('index.html', stream_ids=stream_ids)


######################################################################################################################

# template = """
# <!doctype html>
# <html lang="en">
# <head>
#     <!-- Required meta tags -->
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
#
#     <!-- Bootstrap CSS -->
#     <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
#           integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
#
#     <title>Multiple Live Streaming</title>
# </head>
# <body>
# <div class="container">
#     <div class="row">
#         <div class="col-lg-7">
#             <a>Stream : {{stream}}</a>
#         </div>
#         <div class="col-lg-7">
#             <a>"{{nb_person_predict}}</a>
#         </div>
#         <div class="col-lg-7">
#             <img src="{{predicted_image}}" width="100%">
#         </div>
#     </div>
# </div>
# </body>
# </html>"""


def get_stream_ids():
    return [i for i in range(1, len(streams) + 1)]


def find_stream(stream_id):
    try:
        stream = streams[int(stream_id) - 1]
        print('find_camera stream:', stream)
    except Exception as e:
        print("Camera not found - Error : " + str(e))
        stream = None
    return stream


def get_frame(stream_id, display='predicted_stream'):
    stream = find_stream(stream_id)
    print('gen_frames stream:', stream)
    if stream is None:
        print('yyyyyyyyyyy')
        return None
    print('xxxxxxxxxx')
    try:
        cap = cv2.VideoCapture(stream)
    except Exception as e:
        print("Cannot capture RTSP stream - Error:" + str(e))
        return None
    print('stream captured')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0.0:
        print('fps == 0.0')
        return None
    print('fps:', fps)
    nb_frames_modulo = int(round(snapshot_time * fps, 0))
    print('nb_frames_modulo:', nb_frames_modulo)

    try:
        font = ImageFont.truetype("FreeSerifBold.ttf", size=36)
    except Exception as e:
        print("Cannot load 'FreeSerifBold.ttf' font - error : " + str(e))
        try:
            font = ImageFont.truetype("arial.ttf", size=36)
        except Exception as e:
            print("Cannot load 'arial.ttf' font - error : " + str(e))
            return None

    i_frame = 0
    while True:

        success, frame = cap.read()  # read the camera frame

        if not success:

            print('gen_frames not success')
            break

        else:

            i_frame += 1

            # 1 - une image toutes les nb_frames_modulo secondes
            if (i_frame % nb_frames_modulo) == 0:

                print('gen_frames success frame:', type(frame), frame.shape, len(frame))
                # frame <class 'numpy.ndarray'> (1080, 1920, 3)
                nb_person_predict = 0
                if display_mode == "image_with_density_map":
                    alpha_type = output["alpha_type"]
                    alpha_weight = output["alpha_weight"]
                    factor = output["factor"]

                    # 0 - Convertir la (frame) numpy array to PIL image
                    image = Image.fromarray(frame.astype('uint8'))
                    image = image.convert("RGB")

                    # 2 - Prediction sur l'image
                    nb_person_predict, density_map, _ = ccmodel.predict(image)
                    print('nb_person_predict: ', nb_person_predict)
                    print('density_map.sum(): ', density_map.sum())
                    text_nb_person = str(nb_person_predict) + " personnes"

                    # 3 - Calculer l'image avec la density map
                    img_with_dm, img_dm = image_with_density_map(image,
                                                                 density_map,
                                                                 alpha_type=alpha_type,
                                                                 alpha_weight=alpha_weight,
                                                                 factor=factor)

                    # 4 - Ecrire le nombre de personnes sur l'image
                    draw = ImageDraw.Draw(img_with_dm)
                    draw.text((20, 20), text_nb_person, (0, 255, 0), font=font)

                    # 5 - Convertir l'image en numpy array
                    frame = np.asarray(img_with_dm)

                ret, buffer = cv2.imencode('.jpg', frame)

                if not ret:
                    continue

                print('gen_frames buffer:', type(buffer), buffer.shape, len(buffer))
                # buffer1 <class 'numpy.ndarray'> (826763,) buffer2 <class 'numpy.ndarray'> (827997,)
                frame = buffer.tobytes()
                print('gen_frames len(frame):', len(frame))
                xx = (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                print('XX=', type(xx))
                if display == 'predicted_stream':

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                # elif display == 'stream':
                #     html = template
                #     html = html.replace('{{stream}}', str(stream))
                #     html = html.replace('{{nb_person_predict}}', str(nb_person_predict))
                #     predicted_image = (b'--frame\r\n'
                #                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                #     print('nb_person_predict:', nb_person_predict)
                #     predicted_image = 'xxx'
                #     html = html.replace('{{predicted_image}}', str(predicted_image))
                #
                #     yield html

            # elif (i_frame % int(nb_frames_modulo / 2)) == 0:
            #     ret, buffer = cv2.imencode('.jpg', frame)
            #     if not ret:
            #         continue
            #     frame = buffer.tobytes()
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            else:
                pass
                # print('Skipped frame')


######################################################################################################################

if __name__ == '__main__':
    app.run()
