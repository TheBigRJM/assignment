##### GUI #####

# Create GUI layout elements and structure

column1 = [[sg.Text("Enquiry number:"), sg.InputText(size=2, key="-ENQYEAR-"), sg.InputText(size=3, key="-ENQNO-"), ],
           [sg.Text("----------------------------------------")],
           [sg.Text("Search from Grid Reference or Shapefile")],
           [sg.Text("Grid Reference"), sg.Input('Easting', key="-EASTING-"), sg.Input('Northing', key="-NORTHING-"),
            sg.Text('-OR-'), sg.Text("Shapefile"), sg.Input(key="-BDYFILE-"), sg.FileBrowse()],
           [sg.Text("Search Radius (in metres)"), sg.Input(key="-RADIUS-")]]


column2 = [[sg.Text("Select Search parameters")],
           [sg.Checkbox('Species', default=False, key="-SPP-")],
           [sg.Checkbox('Bats only', default=False, key="-BATS-")],
           [sg.Checkbox('GCN only', default=False, key="-GCN-")],
           [sg.Checkbox('Invasives', default=False, key="-INV-")],
           [sg.Checkbox('Sites', default=False, key="-SITES-")]]

layout = [[sg.Column(column1), sg.VSeparator(), sg.Column(column2)],
          [sg.Button('Proceed', key=("-PROCEED-")), sg.CloseButton('Cancel', key=("-CANCEL-"))]]

# put gui elements in a window
window = sg.Window("Data Search Enquiry", layout, margins=(200, 100))

# event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event=="-CANCEL-":
        print('User cancelled')
        break

    if callable(event):
        event()

    if event == "-GRIDREF-" and event == "-Radius-":
        try:
            point, buffer, buffer_feature = searcharea_frompoint(["-EASTING-"], ["-NORTHING-"], ["-RADIUS-"])

        except:
            print('There was an error')


    if event == "-BDYFILE-" and event == "-Radius-" and event == "-PROCEED-":
        try:
            point, buffer, buffer_feature = searcharea_frompoly(["-BDYFILE-"], ["-RADIUS-"])
            print('bdy, buffer created successfully')

        except:
            print('There was an error')


    if values["-SPP-"] == True and event == "-PROCEED-":
        try:
            sppSearch, sppOutput = searchSpecies
            sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
            plt.show();

        except:
            print("there was an issue")
