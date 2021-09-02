# bbby_btyd

---

A probabilistic approach to estimating customer lifetime value using the "Buy 'Til You Die" methodology via the PyPI Lifetimes package.

Create a docker image from instructions in the Dockerfile to perform a prediction on a single row of data submitted via HTML form (as a demo).

In the directory that holds the Dockerfile, you can run a demo that makes a prediction from data collected via an HTML form.

To build the docker image, run <br/>

docker build -t <image_name> . <br/>
For example,
```
$ docker build -t ltv_image .
```
To create a container from the image, run <br/>

docker run -it --name <container> -p 8080:8080 <image_name> <br/>
For example,
```
$ docker run -it --name ltv_container -p 8080:8080 ltv_image
```
Then navigate to localhost:8080 and you'll be taken to the website's homepage. <br/>
To submit data via an HTML form, simply click on "User Input". <br/>

Have fun!!!

More revisions to follow...

Documentation on the Lifetimes package can be found [here](https://lifetimes.readthedocs.io/en/latest/) or downloaded [here](https://readthedocs.org/projects/lifetimes/downloads/pdf/latest/).

---
Credit to [Cameron Davidson-Pilon (GitHub)](https://github.com/CamDavidsonPilon/lifetimes).
