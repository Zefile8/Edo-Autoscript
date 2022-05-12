import tkinter
import string
import re
import os
from Scripthesaurus import scriptranslate

# script init
filename = "Output (1).lua"
i = 1
while os.path.isfile(filename):
    filename = filename.replace(str(i), str(i+1))
    i += 1
script = open(filename,"w+")
script.write('''--<Card Name>
--<Card Name>
--Edo Autoscript written by Zefile#5500
local s,id = GetID()
function s.initial_effect(c)
	local e1=Effect.CreateEffect(c)
	e1:SetType(<edit settype>)
	e1:SetCode(<edit setcode>)
	<expand effect>
	c:RegisterEffect(e1)
    <expand initial>
end
<add condition>
<add target>
<add operation>
<add func>''')
script.flush()
script.close()

#---------------------------------------------------------------------------
def Scriptit(psct):
    # init needed vars
    psctcopy = psct
    psctcopy = psctcopy.lower()
    convtuple = ("error", 100, "tuple not changed", "")

    # until scriptranslate is out of targets
    while convtuple[1] != 0:
        #find a scriptable bit of psct
        convtuple = scriptranslate(psctcopy)
        #remove scriptable bit from psct
        psctcopy = psctcopy.replace(convtuple[0], "",1)
        
        # stop scripting if an error is returned
        if convtuple[0] == "error":
            print(convtuple)
            return

        # iterate over the replacements to do
        print(convtuple[0])
        for i in range(3, len(convtuple), 2):
            # select output
            with open(filename, 'r') as file :
                filedata = file.read()
            # Replace the target string
            filedata = filedata.replace(convtuple[i-1], convtuple[i], convtuple[1])
            # Write replacement in
            with open(filename, 'w') as file:
                file.write(filedata)
        

    # if psct has text left, print it
    if re.search('[a-z1-9]', psctcopy) is not None:
        print("unable to translate: " + psctcopy)
#---------------------------------------------------------------------------
# tkinter interactive window
window = tkinter.Tk()
window.geometry('280x170+800+400')
window.title("Edo Autoscript")

text1 = tkinter.Text(window, height=8)
text1.pack()
btn1 = tkinter.Button(window, text="Script it!", command=lambda: Scriptit(text1.get("1.0",'end-1c')), width=2000,height=2)
btn1.pack()
window.mainloop()