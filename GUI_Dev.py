##### GUI #####

# Create GUI layout elements and structure

column1 = [[sg.Text("Enquiry number:"), sg.InputText(size=2, key="-ENQYEAR-"), sg.InputText(size=3, key="-ENQNO-"), ],
           [sg.Text("----------------------------------------")],
           [sg.Text("Search from Grid Reference or Shapefile")],
           [sg.Text("Grid Reference"), sg.Input(), sg.Text('-OR-'), sg.Text("Shapefile"), sg.Input(key="-SHPFILE-"),
            sg.FileBrowse()],
           [sg.Text("Search Radius (in metres)"), sg.Input(key="-GRIDREF-")]]


column2 = [[sg.Text("Select Search parameters")],
           [sg.Checkbox('Species', default=False, key="-SPP-")],
           [sg.Checkbox('Bats only', default=False, key="-BATS-")],
           [sg.Checkbox('GCN only', default=False, key="-GCN-")],
           [sg.Checkbox('Invasives', default=False, key="-INV-")],
           [sg.Checkbox('Sites', default=False, key="-SITES-")]]

layout = [[sg.Column(column1), sg.VSeparator(), sg.Column(column2)]]

# put gui elements in a window
window = sg.Window("Data Search Enquiry", layout, margins=(200, 100))

event, values = window.read(close=True)


# event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event=="Exit":
        print('User Cancelled')
        break
    if values["-SPP-"] ==  True
        try :
            searchSpecies


