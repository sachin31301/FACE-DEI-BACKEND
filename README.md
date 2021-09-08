# Face Recognition API

## Python environment

**Python version:** `Python 3.6.8`

For this project, we used `virtualenv` as environment.
You can find it in `API/env`.
You can **activate** it with: 
```bash
$ source env/bin/activate
```
and **disable** it with:
```bash
$ deactivate
```

## Python dependeencies

You can install all the dependencies with:
```bash
$ pip3 install -r requirements.txt
```

```



```
By default it will select the camera of your computer, but you can change it by any video feed, just change the value of `video_capture = VideoCapture(0)` 0 is the prinary webcam of your computer. You can also add multiple feeds.
