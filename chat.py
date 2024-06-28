import sys
from tkinter import *
import customtkinter
import openai
import os
import pickle
from gtts import gTTS
import playsound
import pyaudio
import wave
import speech_recognition as sr
import threading

root = customtkinter.CTk()
root.title("OracleGPT")
root.geometry("620x620")
root.iconbitmap("ai_lt.ico")

no_api = 0

# set color scheme
color = "dark-blue"
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme(color)

# Language in which you want to convert
language = 'en'
event = threading.Event()


def record_audio():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 10
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    read_audio("output.wav")


def read_audio(filename):
    # initialize the recognizer
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        return r.recognize_google(audio_data)


def run_assistant():
    state = True
    my_text.insert(END, f"Establishing mic feed...\n\n")
    while state:
        r = sr.Recognizer()
        if 'normal' == root.state():
            with sr.Microphone() as source:
                print("Tell me something:")
                audio = r.listen(source)
                print(audio)
                if audio:
                    my_text.insert(END, f"Listening...\n\n")
                    try:
                        text = r.recognize_google(audio)
                        print(text)
                        if event.is_set():
                            my_text.insert(END, f"\n\nStopped Listening\n\n")
                            return
                        if "oracle" in text.lower():
                            my_text.insert(END, f"\n\n{text}\n\n")
                            bot_read("api_key", text)
                        elif "stop listening" in text.lower():
                            my_text.insert(END, f"\n\nStopped Listening\n\n")
                            return
                        elif "clear the screen" in text.lower():
                            clear()
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                else:

                    return
        else:
            print("Stopped Listening")
            return


def listen():
    assistant.start()


def speak():
    if chat_entry.get():
        filename = "api_key"
        bot_read(filename, chat_entry.get())


def bot_read(filename, text):
    global no_api
    try:
        if os.path.isfile(filename):
            # open the file
            input_file = open(filename, 'rb')
            # load the data from the file into a variable
            stuff = pickle.load(input_file)

            # query chatGPT
            openai.api_key = stuff
            # create instance
            openai.Model.list()
            # define query
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=text,
                temperature=0,
                max_tokens=60,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            print(response)
            res = (response["choices"][0]["text"]).strip()
            my_text.insert(END, f"{res}\n\n")
            text_to_speech(res)

        else:
            input_file = open(filename, "wb")
            input_file.close()
            os.remove("api_key")
           
            if not no_api:
                my_text.insert(END, "\n\nChatGPT requires an API key. Read aloud mode activated")
                no_api = 1
            if len(text) > 2:
                my_text.insert(END, f"\n\n{text}")
                text_to_speech(text)

    except Exception as e:
        print(f"\n\nAn error occurred: \n\n{e}")


def text_to_speech(res):
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    try:
        engine = gTTS(text=res, lang=language, slow=False)
        # Saving the converted audio in a mp3 file named
        filename = "response.mp3"
        engine.save(filename)

        # Playing the converted file
        playsound.playsound(filename)
        os.remove("response.mp3")
    except Exception as e:
        print(f"\n\nAn error occurred: \n\n{e}")
        text_to_speech(res)


def clear():
    # clear main text box
    my_text.delete(1.0, END)
    # clear entry box
    chat_entry.delete(0, END)


def key():
    filename = "api_key"
    try:
        if os.path.isfile(filename):
            # open the file
            input_file = open(filename, 'rb')

            # load the data from the file into a variable
            stuff = pickle.load(input_file)

            # Output entry stuff
            api_entry.insert(END, stuff)
        else:
            input_file = open(filename, "wb")
            input_file.close()

    except Exception as e:
        print(f"\n\nAn error occurred:\n\n{e}")

    root.geometry("620x720")
    api_frame.pack(pady=10)


def end():
    root.destroy()
    sys.exit()


def save_key():
    filename = "api_key"
    try:
        output_file = open(filename, 'wb')
        # add data to file
        pickle.dump(api_entry.get(), output_file)
        api_entry.delete(0, END)
        api_frame.pack_forget()
        root.geometry("620x620")
        customtkinter.set_default_color_theme("dark-blue")

    except Exception as e:
        print(f"\n\nAn error occurred:\n\n{e}")


assistant = threading.Thread(target=run_assistant)
# Add text frame
text_frame = customtkinter.CTkFrame(root)
text_frame.pack(pady=20)

# get text widget responses
my_text = Text(text_frame,
               bg="#343638",
               width=65,
               bd=1,
               fg="#d6d6d6",
               relief="flat",
               wrap=WORD)
my_text.grid(
    row=0,
    column=0)

# create scroll bar for text widget
text_scroll = customtkinter.CTkScrollbar(text_frame,
                                         command=my_text.yview)
text_scroll.grid(row=0, column=1, sticky="ns")

# add the scrollbar to the text box
my_text.configure(yscrollcommand=text_scroll.set)

# entry widget
chat_entry = customtkinter.CTkEntry(root,
                                    placeholder_text="Allow the oracle to listen or submit text...",
                                    width=535,
                                    height=50,
                                    border_width=1)
chat_entry.pack(pady=10)

# create button frame
button_frame = customtkinter.CTkFrame(root, fg_color="#242424")
button_frame.pack(pady=10)

# create buttons
submit_button = customtkinter.CTkButton(button_frame,
                                        text="Submit",
                                        command=speak)
submit_button.grid(row=0, column=0, padx=24)

listen_button = customtkinter.CTkButton(button_frame,
                                        text="Listen",
                                        command=listen)
listen_button.grid(row=1, column=0, padx=24, pady=10)


api_button = customtkinter.CTkButton(button_frame,
                                     text="Update API Key",
                                     command=key)
api_button.grid(row=1, column=1, padx=24, pady=10)

clear_button = customtkinter.CTkButton(button_frame,
                                       text="Clear",
                                       command=clear)
clear_button.grid(row=0, column=1, padx=24)

exit_button = customtkinter.CTkButton(button_frame,
                                      fg_color=("black", "black"),
                                      text="Exit",
                                      command=end)

exit_button.grid(row=0, column=2, padx=24, pady=10)

# api frame
api_frame = customtkinter.CTkFrame(root, border_width=1)
api_frame.pack(pady=10)

# APi entry widget
api_entry = customtkinter.CTkEntry(api_frame, placeholder_text="Enter API Key",
                                   width=350, height=50, border_width=1)
api_entry.grid(row=0, column=0, padx=20, pady=20)

# Add api button
api_save_button = customtkinter.CTkButton(api_frame,
                                          text="Save Key",
                                          command=save_key)
api_save_button.grid(row=0, column=1, padx=10)
root.mainloop()
