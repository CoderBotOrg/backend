import signal_reader
import main

reader = signal_reader.SignalReader.get_instance()

if __name__=="__main__":
  reader.start()
  main.run_server()
  reader.join()


