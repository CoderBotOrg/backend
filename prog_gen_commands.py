# class Commands
import coderbot
import camera
import motion
import audio
import event
import conversation


class Commands:
    def get_cam():
        return camera.Camera.get_instance()

    def get_bot():
        return coderbot.CoderBot.get_instance()

    def get_motion():
        return motion.Motion.get_instance()

    def get_audio():
        return audio.Audio.get_instance()

    def get_prog_eng():
        return ProgramEngine.get_instance()

    def get_event():
        return event.EventManager.get_instance()

    def get_conv():
        return conversation.Conversation.get_instance()
