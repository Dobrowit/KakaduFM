# --------------------
# This file is used for defining Ttk styles.
# Use the 'style' object to define styles.

# Pygubu Designer will need to know which style definition file
# you wish to use in your project.

# To specify a style definition file in Pygubu Designer:
# Go to: Edit -> Preferences -> Ttk Styles -> Browse (button)

# In Pygubu Designer:
# Assuming that you have specified a style definition file,
# - Use the 'style' combobox drop-down menu in Pygubu Designer
#   to select a style that you have defined.
# - Changes made to the chosen style definition file will be
#   automatically reflected in Pygubu Designer.
# --------------------

# style.py
style.configure('MySpecialButton.TButton',
                font=('helvetica', 12, 'bold'),
                background='green', foreground='white')

style.configure('RedButton.TButton',
                background='red', foreground='white')

style.configure('BlueButton.TButton',
                background='blue', foreground='white')

style.configure('GreenButton.TButton',
                background='green', foreground='white')

style.configure('WhiteButton.TButton',
                background='white', foreground='black')

style.configure('BlackButton.TButton',
                background='black', foreground='white')
