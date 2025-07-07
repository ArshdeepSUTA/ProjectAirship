# for first time running enter these into the terminal
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt



# To deactivate the virtual environment enter
deactivate


# After the first time, to activate the virtual environment just enter the following 
source env/bin/activate


# To run the Airship GUI enter the following line while the virtual environment
python app.py


#For the pi the same can be done exepct to run the server enter
python pi_server.py