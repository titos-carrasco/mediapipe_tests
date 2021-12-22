import cv2
import numpy as np
import json
import queue
import paho.mqtt.client as paho
import time

class FingerMQTT():
    def __init__( self, mqtt_server, mqtt_port, mqtt_topic, img_width, img_height ):
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.img_width = img_width
        self.img_height = img_height
        self.messages = queue.Queue()

    def run( self ):
        mqtt_client = paho.Client()
        mqtt_client.connect( self.mqtt_server, self.mqtt_port )
        mqtt_client.subscribe( self.mqtt_topic )
        mqtt_client.on_message = self.mqtt_on_message
        mqtt_client.on_connect = self.mqtt_on_connect
        mqtt_client.loop_start()

        # comenzamos con una imagen en blanco
        img = np.zeros( ( self.img_height, self.img_width, 3 ), np.uint8 )
        img[:] = ( 255, 255, 255 )
        cv2.imshow( 'Fingers', img )

        # procesamos cada mensaje que nos llegue
        while( True ):
            # si existe un mensaje lo obtenemos
            msg = None
            try:
                msg = self.messages.get_nowait()
            except Exception as e:
                #print( e )
                pass

            # si obtuvimos un mensaje lo procesamos
            if( msg ):
                # obtenemos las marcas de las manos
                manos = json.loads( msg.payload )

                # preparamos una nueva imagen en blanco
                img = np.zeros( ( self.img_height, self.img_width, 3 ), np.uint8 )
                img[:] = ( 255, 255, 255 )

                # agregamos a la imagen las marcas de las manos
                self.addMarks( img, manos )

                # mostramos la imagen con sus marcas
                cv2.imshow( 'Fingers', cv2.flip( img , 1 ) )

            # abortamos con a tecla ESC
            if( cv2.waitKey( 5 ) & 0xFF == 27 ):
                break

        # cerramos todo
        cv2.destroyAllWindows ()
        mqtt_client.loop_stop()

    def mqtt_on_connect( self, client, userdata, flags, rc ):
        client.subscribe( self.mqtt_topic )

    def mqtt_on_message( self, client, userdata, message ):
        self.messages.put_nowait( message )

    def addMarks( self, img, manos ):
        # las marcas
        for mano in manos:
            for mark in mano:
                x = int( round( mark["x"] * self.img_width, 0 ) )
                y = int( round( mark["y"]  * self.img_height, 0 ) )
                cv2.circle( img, ( x, y ), 3, ( 0, 0, 255 ), -1 )

        # las conectamos con lineas
        self.addLine( img, mano[0], mano[1] )
        self.addLine( img, mano[1], mano[2] )
        self.addLine( img, mano[2], mano[3] )
        self.addLine( img, mano[3], mano[4] )

        self.addLine( img, mano[0], mano[5] )
        self.addLine( img, mano[5], mano[6] )
        self.addLine( img, mano[6], mano[7] )
        self.addLine( img, mano[7], mano[8] )

        self.addLine( img, mano[5], mano[9] )
        self.addLine( img, mano[9], mano[10] )
        self.addLine( img, mano[10], mano[11] )
        self.addLine( img, mano[11], mano[12] )

        self.addLine( img, mano[9], mano[13] )
        self.addLine( img, mano[13], mano[14] )
        self.addLine( img, mano[14], mano[15] )
        self.addLine( img, mano[15], mano[16] )

        self.addLine( img, mano[13], mano[17] )
        self.addLine( img, mano[17], mano[18] )
        self.addLine( img, mano[18], mano[19] )
        self.addLine( img, mano[19], mano[20] )

        self.addLine( img, mano[0], mano[17] )
        self.addLine( img, mano[2], mano[5] )

    def addLine( self, img, p1, p2 ):
        x1 = int( round( p1["x"] * self.img_width, 0 ) )
        y1 = int( round( p1["y"]  * self.img_height, 0 ) )
        x2 = int( round( p2["x"] * self.img_width, 0 ) )
        y2 = int( round( p2["y"]  * self.img_height, 0 ) )
        cv2.line( img, ( x1, y1 ), ( x2, y2 ), ( 0, 0, 255 ), 1 )


# show time
o = FingerMQTT( "localhost", 1883, "rcr/myfingers", 640, 480 )
o.run()
