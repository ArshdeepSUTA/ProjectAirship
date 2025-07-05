import Flaskapp
import time
import threading


#flask app (networking) thread function, starts the flask app in its own special thread
def runFlaskApp():
    print("Running Flask app...")
    Flaskapp.app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    print("Starting Blimp controller program")

    #starting networking
    print("Starting Flask app as a thread...")
    flaskThread = threading.Thread(target=runFlaskApp)
    flaskThread.daemon = True
    flaskThread.start()


    