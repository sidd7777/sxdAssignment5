from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import nltk

nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)
app.config["SECRET_KEY"] = "SecureSecretKey"


def clean_files():
    input_directory = "static"  # Specify the input directory
    output_directory = os.path.join(
        "static", "clean_files"
    )  # Specify the output directory

    input_files = [
        filename
        for filename in os.listdir(input_directory)
        if filename.endswith(".txt")
    ]

    porter_stemmer = PorterStemmer()
    tokenizer = RegexpTokenizer(r"\w+")
    stop_words = set(stopwords.words("english"))

    os.makedirs(
        output_directory, exist_ok=True
    )  # Create the output directory if it doesn't exist

    for input_file_name in input_files:
        input_file_path = os.path.join(input_directory, input_file_name)
        output_file_path = os.path.join(output_directory, input_file_name)

        with open(input_file_path, "r", encoding="utf8") as input_file:
            text = input_file.read()
            text = text.encode(
                "ascii", "ignore"
            ).decode()  # Remove non-ASCII characters
            text = text.lower()  # Convert to lowercase
            tokens = tokenizer.tokenize(text)
            filtered_words = [word for word in tokens if word.lower() not in stop_words]
            stemmed_words = [porter_stemmer.stem(word) for word in filtered_words]
            cleaned_text = " ".join(stemmed_words)

        with open(output_file_path, "w", encoding="utf8") as output_file:
            output_file.write(cleaned_text)


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        input_search = request.form.get("input_search")
        if input_search:
            output_results = search_documents(input_search)
        else:
            output_results = []
        return render_template("index.html", output_results=output_results)

    return render_template("index.html")


class NewSearchForm(FlaskForm):
    input_search = StringField("Search Query", validators=[DataRequired()])
    file_name = StringField("File Name", validators=[DataRequired()])
    submit = SubmitField("Search")


@app.route("/search", methods=["GET", "POST"])
def searchForm():
    form = NewSearchForm()
    if form.validate_on_submit():
        try:
            search_word = form.input_search.data
            file_name = form.file_name.data

            # Check if the entered file exists
            file_path = f"static/{file_name}"
            if not os.path.exists(file_path):
                error = f"File '{file_name}' does not exist."
                return render_template("search.html", form=form, error=error)

            output_results = []
            count = 0

            with open(file_path, encoding="utf8") as file:
                lines = file.readlines()
                for line_num, line in enumerate(lines, start=1):
                    if search_word.lower() in line.lower():
                        result = (line.strip(), line.lower().count(search_word.lower()))
                        output_results.append(result)
                        count += result[1]

            return render_template(
                "search.html", output_results=output_results, count=count, form=form
            )

        except Exception as e:
            print(e)
            return render_template("search.html", form=form, error=e)

    return render_template("search.html", form=form)


def search_documents(query):
    cleaned_files_dir = os.path.join("static", "clean_files")
    output_results = []

    for file_name in os.listdir(cleaned_files_dir):
        file_path = os.path.join(cleaned_files_dir, file_name)
        with open(file_path, "r", encoding="utf8") as file:
            lines = file.readlines()
            for line_num, line in enumerate(lines, start=1):
                if query.lower() in line:
                    result = {
                        "file_name": file_name,
                        "line_num": line_num,
                        "line": line.strip(),
                    }
                    output_results.append(result)

    return output_results


if __name__ == "__main__":
    clean_files()
    app.run(debug=True, port=8080)
