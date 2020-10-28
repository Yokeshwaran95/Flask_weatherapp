from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
import os

app=Flask(__name__)

db=SQLAlchemy(app)

class Weather(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	city=db.Column(db.String(200),nullable=False)
	date=db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
	temperature=db.Column(db.Integer)
	description=db.Column(db.String(200))
	icon=db.Column(db.String(200))

	def __repr__(self):
		return (self.city)

@app.route("/")
def index_get():
	weather_list=Weather.query.all()
	return render_template("weather.html",weather=weather_list)

@app.route("/", methods=["POST"])
def index_post():
	weather_list=[]

	url='http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
	
	
	city=request.form.get("city")
	try:
		cities=Weather.query.filter_by(city=city).first()
		if cities:
			err_msg="Location already exists in database"
		else:
			err_msg="Location Added"
			r=requests.get(url.format(city)).json()
			weather={
			"city":city,
				"temperature": r["main"]["temp"],
				"description": r["weather"][0]["description"],
				"icon":r["weather"][0]["icon"],
				}
			new_weather=Weather(city=city,temperature=weather["temperature"],description=weather["description"],icon=weather["icon"])
			db.session.add(new_weather)
			db.session.commit()
			weather_list=Weather.query.all()

	except KeyError:
		err_msg="City does not exist"
	if err_msg:
		flash(err_msg,'error')
		print("error")
	else:
		flash(err_msg,"Location added")
	return redirect(url_for("index_get"))



if __name__=='__main__':

	app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///weather.db"
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
	app.config["DEBUG"]=True
	app.config["SECRET_KEY"]=os.urandom(64)
	db.create_all()
	app.run(debug=True)
