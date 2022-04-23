import tkinter
import string
import re
from Scripthesaurus import scriptranslate

# script init
script = open("Output.lua","w+")
script.write('''--<Card Name>
--Edo Autoscript written by Zefile#5500
local s,id = GetID()
function s.initial_effect(c)
	local e1=Effect.CreateEffect(c)
	e1:SetType(<edit settype>)
	e1:SetCode(<edit setcode>)
	<expand effect>
	c:RegisterEffect(e1)
end
<add condition>
<add target>
<add activate>
<add func>''')
script.flush()
script.close()

#---------------------------------------------------------------------------
def Scriptit(psct):
    # init needed vars
    psctcopy = psct
    psctcopy.lower()
    convtuple = ("error", "tuple not changed", "")

    # until scriptranslate is out of targets
    while convtuple[1] != "":
        convtuple = scriptranslate(psctcopy)
        # remove the scripted bit from the psct
        psctcopy = psctcopy.replace(convtuple[0], "")
        print(convtuple[0])
        
        # iterate over the replacements to do
        for i in range(2, len(convtuple), 2):
            # select output
            with open('Output.lua', 'r') as file :
                filedata = file.read()
            # Replace the target string
            filedata = filedata.replace(convtuple[i-1], convtuple[i])
            # Write replacement in
            with open('Output.lua', 'w') as file:
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