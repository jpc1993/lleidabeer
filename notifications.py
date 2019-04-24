import telepot
from telepot.loop import MessageLoop


class Notification(object):
    """Notification class, includes text and criticity


    """
    def __init__(self, text="", criticity=0):
        super(Notification, self).__init__()
        self.text = text
        self.criticity = criticity

    # @param text The text of the Notification
    def set_text(self, text):
        """Sets the text of the notification
        """
        self.text = text

    def set_criticity(self, criticity):
        self.criticity = criticity


class Command(object):
    """Command"""
    def __init__(self):
        super(Command, self).__init__()

class Channel(object):
    """Channel Class"""
    def __init__(self):
        super(Channel, self).__init__()

class TelegramChannel(Channel):
    """docstring for TelegramChannel."""
    def __init__(self, token, userid, command_list = None):
        super(TelegramChannel, self).__init__()
        self.bot = telepot.Bot(token)
        MessageLoop(self.bot, self.handle).run_as_thread()
        self.userid = userid
        self.command_list = command_list

    def send_notification(self, notification):
        self.bot.sendMessage(self.userid,"* "+str(notification.criticity)+" "+notification.text)


    def handle(self, msg):
            content_type, chat_type, chat_id = telepot.glance(msg)
            if content_type == 'text':
                command = msg['text']
                
                if command[0] == '/':
                    if command == '/help':
                        
                        self.bot.sendMessage(self.userid,"You have an explication" +
                                                          " of the commands in the readme.txt file")
                        return
                    else:
                        parts = command.split(" ")
                        if parts[0] in self.command_list:
                            # TODO: check length (no subcommand)
                            if len(parts) < 2:
                                parts.append("*")
                            if parts[1] in self.command_list[parts[0]]:
                                message = ""
                                for f in self.command_list[parts[0]][parts[1]]:
                                    pmessage = f(msg)
                                    message = message + " " + str(pmessage)+"\n"
                                self.bot.sendMessage(chat_id, message)
                                return
                self.bot.sendMessage(chat_id, 'NOT UNDERSTOOD:' + command + ' /help to view the commands')
               

class ScreenChannel(Channel):
    """docstring for Screen."""
    def __init__(self):
        super(ScreenChannel, self).__init__()

    def send_notification(self, notification):
        print("* "+str(notification.criticity)+" "+notification.text)


if __name__ == "__main__":
    screen = ScreenChannel()
    telegram = TelegramChannel("650160973:AAEzmWv1PwD67PqS3oD290BX_YnWLoGOtRI", 141990140 )
    notification = Notification("This the start test", 1)
    screen.send_notification(notification)
    telegram.send_notification(notification)
