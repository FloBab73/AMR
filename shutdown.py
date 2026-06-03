from naoqi import ALProxy
from time import sleep

ip = "192.168.0.193"
tts = ALProxy("ALTextToSpeech", ip, 9559)
motion = ALProxy("ALMotion", ip, 9559)
autonomusLife = ALProxy("ALAutonomousLife", ip, 9559)

# sit down
autonomusLife.setState("disabled")
