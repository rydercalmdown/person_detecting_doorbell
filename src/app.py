import os
import logging
import threading
import time
import subprocess
from rtsparty import Stream
from objectdaddy import Daddy


logging.basicConfig()
logging.getLogger('logger').setLevel(logging.INFO)


class Doorbell():

    def __init__(self):
        logging.info('Starting doorbell')
        self.person_at_door = False
        self.doorbell_ring_timeout = 5
        self._setup_stream()
        self._setup_object_recognition()

    def _setup_stream(self):
        """Set up the stream to the camera"""
        logging.info('Starting stream')
        self.stream = Stream(os.environ.get('STREAM_URI'))

    def _setup_object_recognition(self):
        """Set up object recognition and load models"""
        logging.info('Loading ML models')
        self.daddy = Daddy()
        self.daddy.set_callbacks(self.object_detected, self.object_expired)

    def object_detected(self, detection):
        """Callback for an object being detected"""
        logging.info(f'{detection.label} detected')
        try:
            if detection.is_person():
                self.person_at_door = True
        except Exception:
            pass

    def object_expired(self, detection):
        """Callback for an object expiring"""
        logging.info(f'{detection.label} expired')
        try:
            if detection.is_person():
                self.person_at_door = False
        except Exception:
            pass

    def ring_doorbell(self):
        """Plays the doorbell sound effect"""
        logging.info('Ringing doorbell')
        base_dir = os.path.dirname(os.path.realpath(__file__))
        doorbell_audio = os.path.join(base_dir, 'audio/doorbell.mp3')
        subprocess.call(['mpg321', doorbell_audio])

    def doorbell_listener(self):
        """Listens for the change of self.person_at_door"""
        while True:
            if self.person_at_door:
                self.ring_doorbell()
                time.sleep(self.doorbell_ring_timeout)
            else:
                time.sleep(0.5)

    def start_doorbell_listener_thread(self):
        """Starts the doorbell_listener function in a background thread"""
        server_thread = threading.Thread(name='doorbell_listener', target=self.doorbell_listener)
        server_thread.setDaemon(True)
        server_thread.start()

    def process_frames_from_stream(self):
        """Processes the frames from the stream"""
        while True:
            frame = self.stream.get_frame()
            if self.stream.is_frame_empty(frame):
                continue
            self.latest_frame = frame
            results, frame = self.daddy.process_frame(frame)

    def run(self):
        """Run the application"""
        self.start_doorbell_listener_thread()
        try:
            self.process_frames_from_stream()
        except KeyboardInterrupt:
            logging.info('Exiting application')


if __name__ == '__main__':
    db = Doorbell()
    db.run()
