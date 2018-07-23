from game import Board
from ai import MineSweeper
from flask import Flask, redirect
import json
app = Flask(__name__)

class HTMLBoard(Board):
    def formatNumber(self, n):
        colours = {1: "#0000ff",
                   2: "#00ff00",
                   3: "#ff0000",
                   4: "#800080",
                   5: "#800000",
                   6: "#40e0d0",
                   7: "#000000",
                   8: "#808080"}
        return "<a style=\"color: {0}; font-weight: bold;\">{1}</a>".format(colours[n], n)

    def cellHTMLInteractive(self, x, y):
        visible = self.visible[(x, y)]
        value = self.board[(x, y)]
        rawHTML = "<td class=\"{0}\" id=\"({1}, {2})\" ondblclick=\"clicked(this);\" onclick=\"flag(this);\">&nbsp;{3}&nbsp;</td>"
        content = ""
        _class = 'invisible'
        if value is not None and value != 0:
            content = self.formatNumber(value)
        if visible:
            _class = 'visible'
        return rawHTML.format(_class, x, y, content)

    def cellHTMLUninteractive(self, x, y):
        visible = self.visible[(x, y)]
        value = self.board[(x, y)]
        rawHTML = "<td class=\"{0}\" id=\"({1}, {2})\">&nbsp;{3}&nbsp;</td>"
        content = ""
        _class = 'invisible'
        if value is not None and value != 0:
            content = self.formatNumber(value)
        if visible:
            _class = 'visible'
        return rawHTML.format(_class, x, y, content)

    def htmlInteractive(self):
        html = """
        <html>
            <head>
                <script>
                    var clicked = function(obj) {
                        var xhr = new XMLHttpRequest();
                        var location = obj.id;
                        xhr.open('GET', '/' + location, true);
                        xhr.onload = function () {
                            var data = xhr.response;
                            uncovered = JSON.parse(data)['uncovered'];
                            state = JSON.parse(data)['state'];
                            if (state == 'defeat'){
                                document.documentElement.innerHTML = "LMAO U LOOZAH";
                            }
                            if (state == 'victory'){
                                document.documentElement.innerHTML = "WINNER!";
                            }
                            for (i = 0; i < uncovered.length; i++){
                                document.getElementById(uncovered[i]).className='visible';
                            };
                        };
                        xhr.send(null);
                    };
                    var flag = function(obj) {
                        if (obj.classList.contains("flagged")){
                            obj.classList.remove("flagged");
                            console.log("Unflagging " + obj.id);
                        }
                        else {
                            obj.classList.add("flagged");
                            console.log("Flagging " + obj.id);
                        };
                    };
                </script>
                <style>
                        table {
                            margin: auto;
                            border-collapse: separate;
                            background: #cccccc;
                            table-layout: fixed;
                        }
                        .invisible {
                            width: 20px;
                            height: 20px;
                            vertical-align: middle;
                            text-align: center;
                            backgroud: #aaaaaa;
                            font-size: 0;
                            border: 2px outset;
                            border-radius: 5px
                        }
                        .visible {
                            width: 20px;
                            height: 20px;
                            vertical-align: middle;
                            text-align: center;
                            border: 1px solid #aaaaaa;
                            border-radius: 5px
                        }
                        .flagged {
                            background: #ee2222;
                        }
                </style>
            </head>
            <body>
                <table>
        """
        for y in range(self.height):
            html += "<tr>"
            for x in range(self.width):
                html += self.cellHTMLInteractive(x, y);
            html += "</tr>"
        html += "</table></body></html>"
        return html

    def htmlUninteractive(self):
        html = """
        <html>
            <head>
                <script>
                    var update = function() {
                        var xhr = new XMLHttpRequest();
                        xhr.open('GET', '/step', true);
                        xhr.onload = function () {
                            var data = xhr.response;
                            uncovered = JSON.parse(data)['uncovered'];
                            state = JSON.parse(data)['state'];
                            if (state == 'defeat'){
                                document.documentElement.innerHTML = "LMAO U LOOZAH";
                            }
                            if (state == 'victory'){
                                document.documentElement.innerHTML = "WINNER!";
                            }
                            for (i = 0; i < uncovered.length; i++){
                                document.getElementById(uncovered[i]).className='visible';
                            };
                        };
                        xhr.send(null);
                    };
                </script>
                <style>
                        table {
                            margin: auto;
                            border-collapse: separate;
                            background: #cccccc;
                            table-layout: fixed;
                        }
                        .invisible {
                            width: 20px;
                            height: 20px;
                            vertical-align: middle;
                            text-align: center;
                            backgroud: #aaaaaa;
                            font-size: 0;
                            border: 2px outset;
                            border-radius: 5px
                        }
                        .visible {
                            width: 20px;
                            height: 20px;
                            vertical-align: middle;
                            text-align: center;
                            border: 1px solid #aaaaaa;
                            border-radius: 5px
                        }
                </style>
            </head>
            <body>
                <button onclick="update();">Update</button>
                <table>
        """
        for y in range(self.height):
            html += "<tr>"
            for x in range(self.width):
                html += self.cellHTMLUninteractive(x, y);
            html += "</tr>"
        html += "</table></body></html>"
        return html

@app.route("/")
def index():
    return redirect("/reset")

@app.route("/(<int:x>, <int:y>)")
def dig(x, y):
    uncovered = board.dig(x, y)
    if board.victory():
        return json.dumps({'uncovered': [], 'state': 'victory'})
    if uncovered is not None:
        return json.dumps({'uncovered': list([str(t) for t in uncovered]), 'state': 'ongoing'})
    else:
        return json.dumps({'uncovered': [], 'state': 'defeat'})

@app.route("/newgame/<int:w>/<int:h>/<int:b>")
def newgame(w, h, b):
    global board
    board = HTMLBoard(w, h, b)
    return board.htmlInteractive()

@app.route("/ai/<int:w>/<int:h>/<int:b>")
def ai(w, h, b):
    global board, minesweeper
    board = HTMLBoard(w, h, b)
    minesweeper = MineSweeper(board)
    return board.htmlUninteractive()

@app.route("/step")
def step():
    uncovered = minesweeper.step()
    if board.victory():
        return json.dumps({'uncovered': [], 'state': 'victory'})
    if uncovered is not None:
        return json.dumps({'uncovered': list([str(t) for t in uncovered]), 'state': 'ongoing'})
    else:
        return json.dumps({'uncovered': [], 'state': 'defeat'})

if __name__ == "__main__":
    app.run(debug = True)
