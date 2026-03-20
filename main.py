# coding=utf8
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import jsonify
import os
import sys
import base64
import sqlite3

#saves current text to temp file named ligma
def ligma(text):
    with open("ligma.txt","w") as f:
        f.write(text)
        f.close()

#adds to database
def add(name,content):
    con = sqlite3.connect("Saved_Files.db")
    temp = "INSERT INTO RECORDS (Name,Record) VALUES('{}','{}')".format(str(name),str(content))
    con.execute(temp)
    con.commit()
    con.close()

#deletes from databse
def delete(primary_key):
    con = sqlite3.connect("Saved_Files.db")
    temp = "DELETE FROM Records WHERE Name = '{}'".format(str(primary_key))
    con.execute(temp)
    con.commit()
    con.close()

#updates the database
def updateDatabase(primary_key,Name,Record):
    con = sqlite3.connect("Saved_Files.db")
    temp = "UPDATE Records SET Name = '{}', Record = '{}' WHERE Name = '{}'".format(str(Name),str(Record),str(primary_key))
    con.execute(temp)
    con.commit()
    con.close()
    pass

#gives all the data from the database
def database():
    con = sqlite3.connect("Saved_Files.db")
    data = [i for i in con.execute("SELECT * FROM Records")]
    con.close()
    return data

app = Flask(__name__,
        static_url_path='', 
        static_folder='static')

# Routes / to index.html (User interface)
@app.route("/")
def home():
    return render_template('index.html')

# The translator function. Handles the entire translation process basically.
@app.route("/text/<text>", methods=["GET", "POST"])
def translateBraille(text):
    ligma(text)
    outputBraille = ""
    # Braille has no upper or lower case so we convert everything to lower.
    text = text.lower()

    # Dictionary of braille characters to english/ascii characters.
    brailleDict = {
        "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙",
        "e": "⠑", "f": "⠋", "g": "⠛", "h": "⠓",
        "i": "⠊", "j": "⠚", "k": "⠅", "l": "⠇",
        "m": "⠍", "n": "⠝", "o": "⠕", "p": "⠏",
        "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
        "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭",
        "y": "⠽", "z": "⠵", "0": "⠚", "1": "⠁",
        "2": "⠃", "3": "⠉", "4": "⠙", "5": "⠑",
        "6": "⠋", "7": "⠛", "8": "⠓", "9": "⠊",
        ",": "⠂", ";": "⠆", ":": "⠒", ".": "⠲",
        "?": "⠦", "!": "⠖", "‘": "⠄", "“": "⠄⠶",
        "“": "⠘⠦", "”": "⠘⠴", "‘": "⠄", "’": "⠄",
        "(": "⠐⠣", ")": "⠐⠜", "/": "⠸⠌", "\\": "⠸⠡",
        "-": "⠤", " ": " ", "%": "⠨⠴", "@": "⠈⠁", "$": "⠈⠎", "'": "⠄"
    }
    isNumber = False
    quoteLocation = -1
    try:
        # Translate character by character.
        for i in text:

            # Handles next line characters.
            if i == "\n":
                outputBraille += "\n"
                continue
            
            # Quotations have special behaviour in braille. Single quote mark is different if it has a corresponding closing mark.
            # This function handles replacing the quotation character based on the previously stored quoteLocation
            if i == '"':
                if quoteLocation == -1:
                    quoteLocation = len(outputBraille)
                    outputBraille += "⠠⠶"
                else:
                    tempOutput = list(outputBraille)
                    tempOutput[quoteLocation] = ""
                    tempOutput[quoteLocation + 1] = "⠦"
                    tempOutput.append("⠴")
                    outputBraille = "".join(tempOutput)
                continue
            
            # Numbers have a special character to denote that it is a number.
            if i.isdigit() and isNumber:
                outputBraille += brailleDict[i]
            elif i.isdigit():
                isNumber = True
                outputBraille += "⠼"
                outputBraille += brailleDict[i]
            elif isNumber:
                isNumber = False
                if i == " ":
                    outputBraille += " "
                else:
                    outputBraille += "⠰"
                    outputBraille += brailleDict[i]
            else:
                if i in brailleDict:
                    outputBraille += brailleDict[i]
    except Exception:

        # In case anything fails or an unhandleable character is present, show an error message
        return "Text contains character that is not recognised."
    return outputBraille


    # Save translated content to file
    f = open("./output.txt", "w")
    f.write(content)
    f.close()
    # Send file as response to request.
    return send_file("./output.txt", as_attachment=True),os.remove("./output.txt")

# Basic Base64 decode function
def decodeBase64(text):
    base64_message = text
    base64_bytes = base64_message.encode('utf8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf8')
    return message

#Input to database
@app.route("/search")
def search():
    f = open("ligma.txt","r+")
    text = f.readlines()[0]
    braille = translateBraille(text)
    return render_template('search.html', text = text, braille = braille)

#Check for conflicting data
@app.route("/namesave", methods=["GET", "POST"])
def respond():
    data = database()
    Name = { "Name":[i[0] for i in data]}
    nameReceived = request.form["Name"]
    f = open("ligma.txt","r+")
    text = f.readlines()[0]
    braille = translateBraille(text)

    if nameReceived not in Name["Name"]:
        add(nameReceived,text)
        return render_template("nameAvailable.html", nameStatus = "Successful Submission to Database")
    else:
        return render_template("search.html", no = "Name is already taken", text = text, braille = braille)

#Displays Records
@app.route("/records")
def records():
    data = database()
    Name = [i[0] for i in data]
    Records = [i[1] for i in data]
    Braille = [translateBraille(i[1]) for i in data]
    records = []
    for i in range(len(Name)):
        records.append([Name[i],Records[i],Braille[i]])
 
    return render_template("records.html", records = records)

@app.route("/update", methods=["GET", "POST"])
def update():
    action = request.form["action"]
    Id = request.form["fromname"]
    IdToChange = request.form["toname"]
    record = request.form["fromrecord"]
    recordToChange = request.form["torecord"]

    data = database()
    Name = [i[0] for i in data]
    print(Name)
    print(Id)

    if Id not in Name:
        return render_template("recordAvailable.html")
    if action == "delete":
        delete(Id)
    if action == "update":
        updateDatabase(Id,IdToChange,recordToChange)
    return records()
if __name__ == "__main__":
    app.run(debug=True)

