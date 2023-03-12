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


root = customtkinter.CTk()
root.title("ChatGPT Bot")
root.geometry("600x560")
root.iconbitmap("ai_lt.ico")

# set color scheme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# submit to chatGPT

# Language in which you want to convert
language = 'en'


def record_audio():
    chunk = 5  # Record in chunks of 1024 samples
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


def speak():
    if chat_entry.get():
        filename = "api_key"
        bot_read(filename, chat_entry.get())
    else:
        record_audio()
        filename = "api_key"
        bot_read(filename, read_audio("output.wav"))
        os.remove("output.wav")


def bot_read(filename, text):
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

            res = (response["choices"][0]["text"]).strip()
            my_text.insert(END, res)
            my_text.insert(END, "\n\n")
            text_to_speech(res)

        else:
            input_file = open(filename, "wb")
            input_file.close()
            my_text.insert(END, "\n\nChatGPT requires an API key.")

    except Exception as e:
        my_text.insert(END, f"\n\nAn error occurred: \n\n{e}")
# submit to chatGPT


def text_to_speech(res):
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=res, lang=language, slow=False)
    # Saving the converted audio in a mp3 file named
    filename = "response.mp3"
    myobj.save(filename)
    # Playing the converted file
    playsound.playsound(filename)
    os.remove(filename)


def clear():
    # clear main text box
    my_text.delete(1.0, END)
    # clear entry box
    chat_entry.delete(0, END)


# submit to chatGPT


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
        my_text.insert(END, f"\n\nAn error occurred:\n\n{e}")

    root.geometry("600x660")
    api_frame.pack(pady=10)


# submit to chatGPT
def save_key():
    filename = "api_key"
    try:
        output_file = open(filename, 'wb')
        # add data to file
        pickle.dump(api_entry.get(), output_file)
        api_entry.delete(0, END)
        api_frame.pack_forget()
        root.geometry("600x560")
        customtkinter.set_default_color_theme("dark-blue")

    except Exception as e:
        my_text.insert(END, f"\n\nAn error occurred:\n\n{e}")


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
                                    placeholder_text="Click submit to record audio.",
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

clear_button = customtkinter.CTkButton(button_frame,
                                       text="Clear Response",
                                       command=clear)
clear_button.grid(row=0, column=2, padx=24)

api_button = customtkinter.CTkButton(button_frame,
                                     text="Update API Key",
                                     command=key)
api_button.grid(row=0, column=3, padx=24)

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
