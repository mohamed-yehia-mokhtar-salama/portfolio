from flask import Flask, render_template, jsonify, request
import tictactoe as ttt

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    board = data['board']
    player = data['player']

    if ttt.terminal(board):
        return jsonify({"status": "terminal", "winner": ttt.winner(board)})

    move = ttt.minimax(board)
    new_board = ttt.result(board, move)

    return jsonify({"board": new_board, "move": move})

if __name__ == "__main__":
    app.run(debug=True)