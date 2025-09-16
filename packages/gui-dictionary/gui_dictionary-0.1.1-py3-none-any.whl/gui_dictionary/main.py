import tkinter
from tkinter import ttk

from gui_dictionary.utils.dictionary import get_antonyms, get_definition, get_synonyms


def main():
    root = tkinter.Tk()

    root.title("Dictionary")
    root.geometry("1080x720")

    definition = ttk.Label(root, wraplength=300, justify="left")

    thesaurus = ttk.Label(root)

    word = tkinter.Variable()

    word_input = ttk.Entry(root, textvariable=word)
    word_input.grid(row=0, column=0, padx=5, pady=5)

    define_button = ttk.Button(
        root, text="Define!", command=lambda: get_definition(definition, word.get())
    )
    define_button.grid(row=0, column=1, padx=5, pady=5)

    synonym_button = ttk.Button(
        root, text="Get Synonyms!", command=lambda: get_synonyms(thesaurus, word.get())
    )
    synonym_button.grid(row=2, column=1, padx=5, pady=5)

    antonym_button = ttk.Button(
        root, text="Get Antonyms!", command=lambda: get_antonyms(thesaurus, word.get())
    )
    antonym_button.grid(row=2, column=2, padx=5, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
