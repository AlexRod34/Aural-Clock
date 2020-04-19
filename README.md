# Aural-Clock
Senior Design Team SoundByte

Uses pocketsphinx for speech recognition,and flite for speech synthesis.
CMUSphinx, pocketsphinx, pigpio library and flite must be downloaded and installed. Use Sphinx Knowledge Base Tool to generate the .lm and .dict files from a sentence corpus file; must be in the correct directory for .lm and .dic as shown in the listenVoice() function. 
Must run "sudo pigpiod" before running python script for GPIO daemon to start.
Then to execute: "python2.7 speakHCUPDATED.py"

Button Functionality: Get current time, volume up/down, alarm reset, alarm adjustment, current time adjustment.


Speech Recognition Functionality: User must say "Okay pi" to prompt the Pi to analyze the speech on the next occurence (will hear a beep after the "okay pi" and then user may speak). Can ask " What time is it?", "Alarm on", "Alarm off", "Set alarm to 9:30AM", "Set alarm to 8AM" , or any other variation of "Set alarm to XX:XXAM/PM". 


Speech Synthesis Functionality: Depending on user action, Pi will respond with speech feedback using flite (text to speech synthesis engine that is a lightweight version of festival)
