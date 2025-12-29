from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# ------------------ MONGODB CONNECTION ------------------
client = MongoClient(
    "mongodb+srv://taskuser:taskuser@cluster0.qhqy1zr.mongodb.net/taskflow_db"
    "?retryWrites=true&w=majority",
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000
)

db = client["taskflow_db"]
tasks = db["tasks"]


# ------------------ ROUTES ------------------

# Dashboard
@app.route("/")
def dashboard():
    total = tasks.count_documents({})
    completed = tasks.count_documents({"status": "Completed"})
    pending = tasks.count_documents({"status": "Pending"})
    return render_template(
        "dashboard.html",
        total=total,
        completed=completed,
        pending=pending
    )

# Add Task (CREATE)
@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        tasks.insert_one({
            "title": request.form["title"],
            "description": request.form["description"],
            "priority": request.form["priority"],
            "status": "Pending"
        })
        return redirect(url_for("view_tasks"))

    return render_template("add_task.html")

# View Tasks (READ)
@app.route("/tasks")
def view_tasks():
    all_tasks = list(tasks.find())  # IMPORTANT: convert cursor to list
    return render_template("view_tasks.html", tasks=all_tasks)

# Edit Task (UPDATE)
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_task(id):
    task = tasks.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        tasks.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "title": request.form["title"],
                "description": request.form["description"],
                "priority": request.form["priority"],
                "status": request.form["status"]
            }}
        )
        return redirect(url_for("view_tasks"))

    return render_template("edit_task.html", task=task)

# Delete Task (DELETE)
@app.route("/delete/<id>")
def delete_task(id):
    tasks.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_tasks"))

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
