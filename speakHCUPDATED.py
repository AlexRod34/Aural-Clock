#!/usr/bin/python
import pigpio
import subprocess as sub
import os
import sys
import thread
from pocketsphinx import LiveSpeech, get_model_path
model_path = get_model_path()
from datetime import datetime
from word2number import w2n
pi = pigpio.pi()
h1 = pi.serial_open('/dev/ttyS0', 9600)
pi.set_mode(27,pigpio.INPUT) # current time
pi.set_pull_up_down(27, pigpio.PUD_DOWN)
pi.set_mode(5,pigpio.INPUT) # vol up
pi.set_pull_up_down(5, pigpio.PUD_DOWN)
pi.set_mode(6,pigpio.INPUT) # vol down
pi.set_pull_up_down(6, pigpio.PUD_DOWN)
pi.set_mode(17,pigpio.INPUT) # alarm reset(DOES NOT TURN ALARM OFF)
pi.set_pull_up_down(17, pigpio.PUD_DOWN)
alarmF  = False
alarmTime  = "00:00"
playing = False

def readBytes():
	#pi = pigpio.pi()
	#h1 = pi.serial_open('/dev/ttyS0', 9600)
	s = ""
	(b,d) = pi.serial_read(h1,2)
	while d!='\n':
		if d:
			s+=d
		(b,d) = pi.serial_read(h1, 1)
		#if s:
			#print(s)
	#print(s)
	#print(chr(s[0]))
	#print(chr(s[0]) == "T")
	if chr(s[0]) == "T":
		#print("made it inside")
		os.chdir("/home/pi")
        	c = open("timeMob.txt", "w")
        	c.write(str(s[1:]))
        	c.close()
		e = sub.call(['sudo','date', '+%T', '-s', str(s[1:])])
	if str(s[0:2]) == "ON":
		global alarmF
		global alarmTime
		alarmF = True
                alarmTime = str(s[2:]) + ":00"
		print("The alarm is set to ON")
		print(alarmTime)
	elif str(s[0:3]) == "OFF":
                alarmF = False
		print("The alarm is set to OFF")


	retval = os.getcwd()
	#print(retval)
	os.chdir("/home/pi")
	f = open("tmp.txt", "w")
	f.write(str(s[1:]))
	f.close()
	#p = sub.Popen(['festival', '--tts', 'tmp.txt'], stdout=sub.PIPE, stderr=sub.PIPE)
	
	#p = sub.Popen(['cd','flite'], stdout=sub.PIPE, stderr=sub.PIPE)
	os.chdir("/home/pi/flite")
	p = sub.Popen(['./bin/flite','/home/pi/tmp.txt','test.wav'])
	p = sub.Popen(['aplay','test.wav'], stdout=sub.PIPE, stderr=sub.PIPE)
	p.communicate()

def readTime(): # doesnt get called
	if pi.wait_for_edge(27):
		os.chdir("/home/pi")
		#currentTime = time.ctime()
		now = datetime.now()
		currentTime =""
		currentTime = now.strftime("%H:%M:%S")
		f2 = open("curTime.txt", "w")
		f2.write(currentTime)
		f2.close()
		os.chdir("/home/pi/flite")
        	q = sub.Popen(['./bin/flite','/home/pi/curTime.txt','testtime.wav'])
		print(os.getcwd())
        	q = sub.Popen(['aplay','testtime.wav'], stdout=sub.PIPE, stderr=sub.PIPE)
        	q.communicate()		
		print(currentTime)

def keepReadingBT():
	while 1:
		readBytes()
def listenVoice():
	global playing
	global alarmF
	global alarmTime
	while 1:
		# TODO: detect speech and obtain string
		# sets up speech class to listen
		speech = LiveSpeech(
        		audio_device = 'plughw:1,0',
        		verbose = False,
        		sampling_rate = 16000,
        		buffer_size = 2048,
        		no_search = False,
        		full_utt = False,
        		hmm = os.path.join(model_path, 'en-us'),
        		lm = os.path.join(model_path, '4155.lm'), # changed to use new language model .. more words=slower?
        		dic = os.path.join(model_path, '4155.dic') # changed to use new dictionary .. more words=slower?
		)
		for phrase in speech:
			print("listening")
			print(phrase)
			stringP = str(phrase)
			print(stringP[0:4])
			#if 'what time is it/what is the time' is heard
			#print(str(phrase) + "hello")
                	if (str(phrase) == "WHAT TIME IS IT" or str(phrase) == "WHAT IS THE TIME"):
                        	print("what time is it was asked")
                        	os.chdir("/home/pi")
                        	currentTime =""
                        	now = datetime.now()
                        	currentTime = now.strftime("%H:%M:%S")
                        	f2 = open("curTime.txt", "w")
                        	f2.write("The time is " + currentTime[0:5])
                        	f2.close()
                        	os.chdir("/home/pi/flite")
				os.system("./bin/flite /home/pi/curTime.txt testtime.wav")
                        	print(currentTime)
                        	os.system("aplay testtime.wav")
			#if 'alarm time' is heard
			elif str(phrase) == "ALARM TIME":
				print("alarm time was asked")
				os.chdir("/home/pi")
				f2 = open("alarmTime.txt", "w")
				f2.write("The alarm is at " + alarmTime)
				f2.close()
				os.chdir("/home/pi/flite")
				os.system("./bin/flite /home/pi/curTime.txt alarm_time.wav")
                        	print(alarmTime)
                        	os.system("aplay alarm_time.wav")
			#if 'reset alarm/alarm reset' is heard
			elif(str(phrase) == "RESET ALARM" or str(phrase) == "ALARM RESET"):
				playing = False
				print("Playing is false")
			#if 'alarm on/alarm off' is heard
			elif(stringP == "ALARM ON"):
				alarmF = True
				print("Alarm turned on")
			elif(stringP == "ALARM OFF"):
				alarmF = False
				print("Alarm turned off")
			#if 'volume up/volume down' is heard, or 'volume one hundred' 'volume zero'
			elif(str(phrase) == "VOLUME UP"):
				os.system("amixer set Speaker 25%+")
				print("Speaker up by 25%")
			elif(str(phrase) == "VOLUME DOWN"):
				os.system("amixer set Speaker 25%-")
				print("Speaker down by 25%")
			elif(str(phrase) == "VOLUME ONE HUNDRED"):
				os.system("amixer set Speaker 100%")
				print("Speaker set to 100%")
			elif(str(phrase) == "VOLUME ZERO"):
				os.system("amixer set Speaker 0%")
				print("Speaker set to 0%")
			#if 'set alarm to xxxx' or 'set the alarm to' ---- will take some word2num processing to extract correct time
			elif(stringP[0:12] == "SET ALARM TO"):
				wordTime = stringP[13:] # gets time in word format i.e "three twenty one" or "two forty" or "two"
				print("Alarm set to: " + wordTime)
				#need to get alarm time in format: HH:MM -> will need to also get AM or PM at the end
				time = ""
				daynight = str(wordTime.split(" ",-1)[-1])
				hour = str(wordTime.split(" ")[0])
				minute = ""
				#checks if HH is single digit, then pad with 0, else dont
				if(w2n.word_to_num(hour) < 10):
					time = time + "0" + str(w2n.word_to_num(hour))
				else:
					time = time + str(w2n.word_to_num(hour))
				#checks MM if exists and is not the day/night i.e. THREE TWENTY ONE AM, else just pad with 00 
				minute = str(wordTime.split(" ",1)[1])
				if(len(wordTime.split(" ")) > 1 and (minute !="A") and (minute !="AM") and (minute !="P") and (minute !="PM")):
        				if(w2n.word_to_num(minute) < 10):
                				time = time + ":"+ "0" + str(w2n.word_to_num(minute))
        				else:
                				time = time + ":" + str(w2n.word_to_num(minute)) 
				else:
        				time = time + ":" + "00"
				print("Alarm time: " + time + daynight)
				if((daynight =="AM") or (daynight == "A")):
					# correct time for AM time in military time
					if(int(time[0:2]) == 12):		#midnight time
						alarmTime = "00" + time[2:]
					else:
						alarmTime = time
				elif((daynight == "PM") or (daynight == "p")):
					# correct time for PM time in military time
					if(int(time[0:2]) == 12):		#mid day time 
						alarmTime = time
					else:
						tempHourAdjust = 12 + int(time[0:2])
						alarmTime = str(tempHourAdjust) + time[2:]



			#elif(stringP[0:16] == "SET THE ALARM TO")
				#print("Alarm is set to: ")



 		#except BrokenPipeError:
		#devnull = os.open(os.devnull, os.O_WRONLY)
		#os.dup2(devnull, sys.stdout.fileno())
		#sys.exit(1)

def playAlarm():
	global playing
	global alarmF
	while 1:
		nowtime = datetime.now()
                currentTime =""
                currentTime = nowtime.strftime("%H:%M:%S")
		#print("inside playAlarm")
		#print(currentTime[0:5])
		#print(alarmTime)
		#print(alarmF)
		#print(playing)
		if alarmF and alarmTime == currentTime and not playing:
			playing = True
			while playing:
				print("Should start playing")
				os.chdir("/home/pi")
				a = sub.Popen(['aplay','alarmSound.wav'], stdout=sub.PIPE, stderr=sub.PIPE)
                		a.communicate()


def keepReadingTVAButton():
	global playing
	try:
		while 1:
			if (pi.read(27) == 1):
				os.chdir("/home/pi")
                		#currentTime = time.ctime()
                		now = datetime.now()
                		currentTime =""
                		currentTime = now.strftime("%H:%M:%S")
                		f2 = open("curTime.txt", "w")
                		f2.write(currentTime[0:5])
                		f2.close()
                		os.chdir("/home/pi/flite")
                		q = sub.Popen(['./bin/flite','/home/pi/curTime.txt','testtime.wav'])
                		print(os.getcwd())
                		q = sub.Popen(['aplay','testtime.wav'], stdout=sub.PIPE, stderr=sub.PIPE)
                		q.communicate()         
                		print(currentTime)



			if(pi.read(5) == 1):
				os.system("amixer set Speaker 5%+")
			if(pi.read(6) == 1):
				os.system("amixer set Speaker 5%-")
			if pi.read(17) == 1 and playing:
                        	playing = False
			while pi.read(27) == 1:
				print("waiting for time adjustment...")
				if pi.read(5) == 1:
					print("both buttons pressed, minute ++")
					os.chdir("/home/pi")
					time = datetime.now()
					hr = time.hour
					mint = time.minute
					mint += 1
					if mint == 60:
						mint = 0
						hr += 1
					if hr == 24:
						hr = 0
					new_time = time.replace(hour=hr, minute=mint)
					currentTime = new_time.strftime("%H:%M:%S")
					#f2 = open("curTime.txt", "w")
					#f2.write(currentTime)
					#f2.close()
					e = sub.call(['sudo','date', '+%T', '-s', currentTime])
				if pi.read(6) == 1:
					print("both buttons pressed, minute --")
					os.chdir("/home/pi")
					time = datetime.now()
					hr = time.hour
					mint = time.minute
					mint -= 1
					if mint == -1:
						mint = 59
						hr -= 1
					if hr == -1:
						hr = 23
					new_time = time.replace(hour=hr, minute=mint)
					currentTime = new_time.strftime("%H:%M:%S")
					#f2 = open("curTime.txt", "w")
					#f2.write(currentTime)
					#f2.close()
					e = sub.call(['sudo','date', '+%T', '-s', currentTime])

	except Exception as e:
		print(e)
		#keepReadingTVAButton()
if __name__ == "__main__":
	try:
		thread.start_new_thread(keepReadingBT,())
		thread.start_new_thread(keepReadingTVAButton,())
		thread.start_new_thread(playAlarm,())
		listenVoice()
	except Exception as e:
		print(e)
	while 1:
		pass

