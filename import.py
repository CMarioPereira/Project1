import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://pzbwwiazhlckur:9376f8c09de4c84eff9d268156336408ef864152e97e99ce89d49163dc087580@ec2-52-44-166-58.compute-1.amazonaws.com:5432/d8iug83ch38piq")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year":year})
    db.commit()
    print("The books were successfully uploaded!")

if __name__ == "__main__":
    main()
