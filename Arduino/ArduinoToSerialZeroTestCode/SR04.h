#ifndef SR04_H
#define SR04_H

#if defined(ARDUINO) && ARDUINO >= 100
	#include "Arduino.h"
#else
	#include "WProgram.h"
#endif
//#include "pins_arduino.h"

#include <inttypes.h>

#define PULSE_TIMEOUT 150000L	// 100ms
#define DEFAULT_DELAY 10
#define DEFAULT_PINGS 5
class SR04 {
public:
	
	SR04(int echoPin, int triggerPin);


	long Distance();
	
	
private:
	long MicrosecondsToCentimeter(long duration);
	
	long _currentDistance;
	int _echoPin, _triggerPin;
	long _duration, _distance;
	bool _autoMode;
};
#endif



