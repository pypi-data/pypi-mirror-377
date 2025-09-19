import random
import tkinter as tk

# List of Marathi jokes
jokes_list = [
    "शिक्षक: गृहपाठ का केला नाहीस? विद्यार्थी: वीज गेली होती सर! शिक्षक: पण वीजेचा गृहपाठाशी काय संबंध? विद्यार्थी: गुगल चाललं नाही सर! 😅",
    "बायको: काय रे, माझं सौंदर्य पाहून तुला झोपच लागत नाही ना? नवरा: नाही गं, तुझं सौंदर्य पाहिलं की झोप पटकन लागते! 😂",
    "मित्र: आज उशीर का झाला? दुसरा मित्र: स्वप्नात लग्न लागलं होतं, मंडपातून बाहेर पडायला वेळ लागला! 🤣",
    "विद्यार्थी: सर, परीक्षेत कॉपी केल्यावर गुण कमी का केले? सर: कारण तू स्वतःपेक्षा हुशार मुलाकडून कॉपी केली होतीस! 😜"
]

def get_joke():
    return random.choice(jokes_list)

def get_all_jokes():
    return jokes_list

def show_window():
    joke = get_joke()
    root = tk.Tk()
    root.title("Marathi Joke 😅")
    root.geometry("400x200")

    label = tk.Label(root, text=joke, font=("Nirmala UI", 12), wraplength=350, justify="center")
    label.pack(pady=20, padx=10)

    button = tk.Button(root, text="😂 आणखी एक", command=lambda:[root.destroy(), show_window()])
    button.pack(pady=10)

    root.mainloop()
