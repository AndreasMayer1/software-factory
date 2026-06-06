# feedback to requirements_tasks\process\AI_rules\dev_infrastructure\dev_environment\requirements.md


Path C:\private_mood_tracker_mirror\flutter_app\ is fine in the requ if you want it to be developer agnostic. but I want to have the windows copy in the same location it currently is: C:\Users\am-ur\Projekte Lokaler Arbeitsbereich\private_mood_tracker\flutter_app\
that means that "The Windows-side live project location used by earlier configurations is retired" is wrong.
Maybe make a note somewhere that the path in the requirement is just an example?

wring style critique: the requirement reads in parts like a plan, not like a specification. requirements must describe the desired end state ina timeless manner, for example: "if and when these are repaired — they are currently broken and their repair is tracked separately" is not timeless. at least a timestamp would be needed for this claim. maybe we need to refine the requ-explore skill?
sometimes it also reads like a manual. ("USB attachment uses `usbipd attach --wsl --busid <id>` to forward the device from Windows to WSL; wireless attachment uses `adb tcpip 5555` on the device once and `adb connect <ip>:5555` from the container thereafter. The setup guide documents both paths.") Maybe we should allow the requ-explore skill to write additional documents beside the requirements.md file to hold such information, becuase they are very valuable. what do you think? am I too strict?

"Optionality contract for non-supported environments" the optionally is also something i don't like in requirements: "optionally" is it a requirement or is it not?  



