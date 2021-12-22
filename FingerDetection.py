import cv2
import mediapipe as mp
import json
import paho.mqtt.client as paho
import time

def main( video_port,       # el dispositivo de captura
          video_width,      # ancho de la imagen
          video_height,     # alto de la imagn
          mqtt_server,      # servidor MQTT
          mqtt_port,        # puerta MQTT
          mqtt_topic,       # topico MQTT
          tick              # intervalo de envio de mensajes
        ):

    # nos conectamos al servidor MQTT
    mqtt_client = paho.Client()
    mqtt_client.connect( mqtt_server, mqtt_port )
    mqtt_client.loop_start()

    # configuramos la captura de video
    cap = cv2.VideoCapture( video_port )
    cap.set( cv2.CAP_PROP_FRAME_WIDTH, video_width )
    cap.set( cv2.CAP_PROP_FRAME_HEIGHT, video_height )
    capW = cap.get( cv2.CAP_PROP_FRAME_WIDTH )
    capH = cap.get( cv2.CAP_PROP_FRAME_HEIGHT )

    # configuramos la deteccion de las manos
    hands = mp.solutions.hands.Hands(
                static_image_mode = False,
                max_num_hands = 2,
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

    # radio del circulo a usar por cada marca en los dedos

    # comenzamos
    rad = int( round( capW/capH, 0 ) )*4
    t0 = 0
    while cap.isOpened():
        # capturamos la imagen
        success, img = cap.read()
        if( not success ): continue

        # buscamos las manos
        results = hands.process( img )

        # se detectaron manos?
        if results.multi_hand_landmarks:
            manos = []
            for hand_landmarks in results.multi_hand_landmarks:
                fields    = hand_landmarks.ListFields() # sus campos
                hand      = fields[0]                   # la mano
                landmarks = hand[1]                     # sus landmarks
                # obtenemos las coordenadas x, y, z de cada marca
                mano = []
                for mark in landmarks:
                    mano.append( { "x": mark.x, "y": mark.y, "z": mark.z } )
                manos.append( mano )

            # mostramos las marcas
            for mano in manos:
                for mark in mano:
                    x = int( round( mark["x"] * capW, 0 ) )
                    y = int( round( mark["y"]  * capH, 0 ) )
                    cv2.circle( img, ( x, y ), rad, ( 0, 0, 255 ), -1 )

            # si el intervalo de tiempo a pasado entonces las enviamos
            # lo hacemos de esta manera para no acumular imagenes en el buffer de captura
            if( time.time() - t0 > tick ):
                mqtt_client.publish( mqtt_topic, json.dumps( manos ) )
                t0 = time.time()

        # desplegamos la imagen capturad y procesada con olas marcas
        cv2.imshow( 'Fingers', cv2.flip( img , 1 ) )
        if( cv2.waitKey( 5 ) & 0xFF == 27 ):
            break

    # eso es todo
    cap.release()
    cv2.destroyAllWindows ()
    mqtt_client.loop_stop()


# show time
main( 0, 640, 480, "localhost", 1883, "rcr/myfingers", 0.1 )
