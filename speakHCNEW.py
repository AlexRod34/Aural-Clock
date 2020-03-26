#!/usr/bin/python
import pigpio
import subprocess as sub
import os
import thread
#import time
from datetime import datetime
pi = pigpio.pi()
h1 = pi.serial_open('/dev/ttyS0', 9600)
pi.set_mode(27,pigpio.INPUT)
pi.set_pull_up_down(27, pigpio.PUD_DOWN)
pi.set_mode(5,pigpio.INPUT) # vol up
pi.set_pull_up_down(5, pigpio.PUD_DOWN)
pi.set_mode(6,pigpio.INPUT) # vol down
pi.set_pull_up_down(6, pigpio.PUD_DOWN)
pi.set_mode(17,pigpio.INPUT) # alarm reset
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
	while 1:
		# TODO: detect speech and obtain string
		print("Listening for audio...")
		# listens for audio for 3 seconds and saves to speech.wav file
		os.system("sudo arecord --device=hw:1,0 --format S16_LE --rate 48000 -d 3 -c1 /home/pi/speech.wav")
		print("Processing 3 sec audio snippet")
		# calls pocketsphinx to compile the audio using the learning model and dictionary that we specify, and outputs the audio recogonized to an output.txt file
		os.system("pocketsphinx_continuous -samprate 48000 -nfft 2048 -remove_noise yes -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm /usr/local/share/pocketsphinx/model/lm/0476.lm -dict /usr/local/share/pocketsphinx/model/lm/0476.dic -infile /home/pi/speech.wav > /home/pi/output.txt 2>/dev/null")
		print("Done")
		f1 = open("/home/pi/output.txt","r")
		speech = f1.readline()
		f1.close()
		#speech = speech.replace("\n", " ")
		print(speech)
		print(str(speech))

		# if 'reset' is heard
		#playing = False
		index = speech.find("WHAT TIME")
		# if 'what time is it' is heard
		if (index != -1):
			print("what time is it was asked")
			os.chdir("/home/pi")
			currentTime =""
			now = datetime.now()
			currentTime = now.strftime("%H:%M:%S")
			f2 = open("curTime.txt", "w")
			f2.write("The time is " + currentTime[0:5])
			f2.close()
			os.chdir("/home/pi/flite")
			q = sub.Popen(['./bin/flite', '/home/pi/curTime.txt', 'testtime.wav'])
			q = sub.Popen(['aplay', 'testtime.wav'], stdout=sub.PIPE, stderr=sub.PIPE)
			q.communicate()
			print(currentTime)
			os.system("aplay testtime.wav")
			os.system("aplay sampleAll.wav")

		#TODO implement volume control via voice recognition

def playAlarm():
	global playing
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
	while 1:
	#make a delayyyy
		#pigpio.pulse(27, 27, 1000000)
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
try:
	thread.start_new_thread(keepReadingBT,())
	thread.start_new_thread(keepReadingTVAButton,())
	thread.start_new_thread(playAlarm,())
	thread.start_new_thread(listenVoice,())
except:
	print("Error:unable to start thread")
while 1:
	pass

