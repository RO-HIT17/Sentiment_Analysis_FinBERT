import tkinter as tk
from tkinter import *
from improve_txt import *
from functools import partial
import re


def color_positions(analyzed_text_area: Text) -> None:
    """
    Colors suggestion into different color for readability
    :param analyzed_text_area: a Text UI element that contains the text
    :return: None
    """
    text = analyzed_text_area.get(1.0, 'end-1c')

    index = 0
    location = re.search(r'<.*?>', text)

    while location:
        start_i, end_i = location.span()
        analyzed_text_area.tag_add('start', '1.' + str(start_i + index), '1.' + str(end_i + index))

        index = end_i + index + 1
        text = text[end_i + 1:]

        location = re.search(r'<.*?>', text)


def suggest_improvements(user_input_text_area: Text, analyzed_text_area: Text) -> None:
    """
    Implements Text Improvement Engine by taking user input text area and filling and coloring analyzed text area
    :param user_input_text_area: a UI Text element of user input text area
    :param analyzed_text_area: a UI Text element of analyzed text area
    :return: None
    """
    analyzed_text_area.delete(1.0, 'end-1c')

    user_input_text = user_input_text_area.get(1.0, 'end-1c')
    sentence_suggestions, modified_sentences = analyze_txt(user_input_text)

    single_paragraph = ' '.join(modified_sentences)
    analyzed_text_area.insert(tk.END, single_paragraph)
    analyzed_text_area.tag_config('start', foreground='blue')

    color_positions(analyzed_text_area)


def populate_list(standard_terms_list: Listbox) -> None:
    """
    Populates UI List with Standardized terms
    :param standard_terms_list: a Listbox UI element for showing standardized terms
    :return: None
    """
    for i, standard_term in enumerate(standard_terms):
        standard_terms_list.insert(i + 1, standard_term)


def main():
    root = Tk()
    root.title('Text Improvement Engine')
    root.geometry('700x600')

    instruction_label = Label(root, text='Please, write text to suggest improvements')
    instruction_label.config(font=('Courier', 14))
    instruction_label.pack(side=TOP)

    frame = Frame(root)
    frame.pack()

    user_input_text_area = Text(frame, height=15, width=60)
    user_input_text_area.insert(tk.END, sample_txt)
    user_input_text_area.pack(side=LEFT)

    standard_terms_list = Listbox(frame, height=12)
    populate_list(standard_terms_list)
    standard_terms_list.pack(side=LEFT)

    analyzed_text_area = Text(root, height=20, width=60)

    analyze_button = Button(root, fg='green', text='Suggest', command=partial(suggest_improvements,
                                                                              user_input_text_area,
                                                                              analyzed_text_area))
    analyze_button.pack()
    analyzed_text_area.pack()

    tk.mainloop()


if __name__ == '__main__':
    main()

